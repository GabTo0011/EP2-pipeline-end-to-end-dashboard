import os
import sys
import subprocess
import json
import pickle
import logging
from pathlib import Path
import random
from datetime import datetime, timedelta

import streamlit as st
import requests
import pandas as pd

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from contextlib import asynccontextmanager
import psycopg2
from pydantic import BaseModel
import pandas as pd

from app.ml_service import predecir

# Configurar logs para seguir las predicciones
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# Carga de datos desde el archivo JSON montado como volumen en el contenedor
data_file = Path("/app/data/json/api-data.json")
if not data_file.exists():
    data_file = Path(__file__).resolve().parents[2] / "data" / "json" / "api-data.json"

def cargar_datos():
    try:
        with data_file.open("r", encoding="utf-8") as f:
            return json.load(f), 200
    except FileNotFoundError as e:
        return {"mensaje": "El archivo JSON no existe en la ruta especificada.", "status": 404, "error": str(e)}, 404
    except json.JSONDecodeError as e:
        return {"mensaje": "Error de sintaxis o formato en el archivo JSON.", "status": 400, "error": str(e)}, 400


if sys.platform == 'win32':
    try:
        subprocess.run(["chcp", "65001"], shell=True, check=True, stdout=subprocess.DEVNULL)
        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)
    except Exception:
        pass


import time  # Asegúrate de tener esta importación arriba si no está


# class PredictionRequest(BaseModel):
#     comuna_id: int
#     comuna: str
#     ingreso_promedio_hogar: float
#     paradero_id: int
#     latitud: float
#     longitud: float
#     recorrido_id: int
#     recorrido: str
#     empresa_operadora: str
#     capacidad_pasajeros: int
#     flujo_pasajeros: int
#     velocidad_promedio: float
#     hora: int
#     dia: int
#     mes: int

def conectar_bd():
    max_intentos = 5
    intento = 0
    while intento < max_intentos:
        try:
            return psycopg2.connect(
                host=os.getenv("DATABASE_HOST", "127.0.0.1"),
                database=os.getenv("DATABASE_NAME", "movilidad_rm_db"),
                user=os.getenv("DATABASE_USER", "estudiante"),
                password=os.getenv("DATABASE_PASSWORD", "estudiante_password"),
                port=int(os.getenv("DATABASE_PORT", "5432")),
                client_encoding='utf8'
            )
        except Exception as e:
            intento += 1
            print(f"⚠️ Intento {intento}/{max_intentos} fallido. Esperando a PostgreSQL...")
            if intento >= max_intentos:
                print("\n" + "="*50)
                print("¡ERROR DE POSTGRESQL DETECTADO!")
                print(repr(e))
                print("="*50 + "\n")
                raise e
            time.sleep(3)  # Espera 3 segundos antes del siguiente intento


# =====================================================
# CARGA DE MODELOS Y LIFESPAN (FastAPI)
# =====================================================
modelo_supervisado = None
modelo_no_supervisado = None

# Mapeos rápidos para codificar datos de entrada del Dashboard al formato numérico del modelo
comuna_mapping = {"SANTIAGO": 0, "PROVIDENCIA": 1, "LAS CONDES": 2, "MAIPU": 3, "FLORIDA": 4, "PUENTE ALTO": 5}
tipo_dia_mapping = {"LABORAL": 0, "SABADO": 1, "DOMINGO": 2}


@asynccontextmanager
async def lifespan(app: FastAPI):
    global modelo_supervisado, modelo_no_supervisado
    print("Iniciando aplicación, cargando modelos ML y conectando a PostgreSQL...")

    # 1. Cargar Modelos de Machine Learning (.pkl)
    ruta_sup = "/app/models/modelo_regresion.pkl"
    ruta_no_sup = "/app/models/modelo_kmeans.pkl"
    
    # Fallback si estás probando fuera de Docker localmente
    if not os.path.exists(ruta_sup):
        ruta_sup = "models/modelo_regresion.pkl"
        ruta_no_sup = "models/modelo_kmeans.pkl"

    if os.path.exists(ruta_sup) and os.path.exists(ruta_no_sup):
        try:
            with open(ruta_sup, "rb") as f:
                modelo_supervisado = pickle.load(f)
            with open(ruta_no_sup, "rb") as f:
                modelo_no_supervisado = pickle.load(f)
            logging.info("🎉 Modelos de Machine Learning cargados con éxito desde el volumen.")
        except Exception as e:
            logging.error(f"Error al deserializar modelos .pkl: {str(e)}")
    else:
        logging.warning(f"⚠️ No se encontraron archivos de modelos en '{ruta_sup}'. Se activará el simulador.")

    # 2. Inicialización de Tablas de Base de Datos
    try:
        conn = conectar_bd()
    except Exception as e:
        print("\n" + "=" * 60)
        print("[ERROR CRITICO DE CONEXION]")
        error_msg = str(e).encode('utf8', errors='ignore').decode('utf8')
        print(error_msg)
        print("=" * 60 + "\n")
        os._exit(1)

    cur = conn.cursor()

    # Creación de tablas
    cur.execute("""
        CREATE TABLE IF NOT EXISTS comunas(
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            ingreso_promedio_hogar NUMERIC(12,2)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS paraderos(
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(20),
            latitud DECIMAL(10,7),
            longitud DECIMAL(10,7),
            comuna_id INTEGER REFERENCES comunas(id)
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS recorridos(
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50),
            empresa_operadora VARCHAR(100),
            capacidad_pasajeros INTEGER
        );
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS monitoreo_viajes(
            id SERIAL PRIMARY KEY,
            fecha_hora TIMESTAMP,
            paradero_id INTEGER REFERENCES paraderos(id),
            recorrido_id INTEGER REFERENCES recorridos(id),
            tiempo_promedio_viaje DECIMAL(6,2),
            flujo_pasajeros INTEGER,
            velocidad_promedio DECIMAL(5,2)
        );
    """)

    # Datos de prueba
    cur.execute("SELECT COUNT(*) FROM comunas;")
    resultado = cur.fetchone()

    if resultado and resultado[0] == 0:
        # Comunas
        cur.execute("""
            INSERT INTO comunas (nombre, ingreso_promedio_hogar) VALUES
            ('Puente Alto',850000), ('Maipu',950000), ('San Bernardo',800000), ('Pudahuel',900000),
            ('La Florida',1100000), ('Santiago',1400000), ('Providencia',2200000), ('Las Condes',3000000),
            ('Vitacura',3800000), ('Lo Barnechea',4200000);
        """)
        # Paraderos
        cur.execute("""
            INSERT INTO paraderos (codigo, latitud, longitud, comuna_id) VALUES
            ('PA101',-33.6111,-70.5755,1), ('MA102',-33.5100,-70.7600,2), ('SB103',-33.5900,-70.7000,3),
            ('PD104',-33.4400,-70.7400,4), ('LF105',-33.5200,-70.5800,5), ('ST106',-33.4500,-70.6667,6),
            ('PR107',-33.4300,-70.6100,7), ('LC108',-33.4100,-70.5600,8), ('VT109',-33.3900,-70.5700,9),
            ('LB110',-33.3500,-70.5200,10);
        """)
        # Recorridos
        cur.execute("""
            INSERT INTO recorridos (nombre, empresa_operadora, capacidad_pasajeros) VALUES
            ('210','Metbus',120), ('405','STP',100), ('506','Redbus',110), ('301','Vule',115),
            ('712','Metbus',120), ('Metro L1','Metro',1000), ('Metro L4','Metro',1000),
            ('Metro L5','Metro',1000), ('Metro L6','Metro',1000), ('Metro L3','Metro',1000);
        """)

        # Históricos
        fecha_base = datetime(2025, 1, 1, 0, 0)
        zonas_laborales = [6, 7, 8, 9]
        zonas_residenciales = [1, 2, 3, 4, 5]

        for i in range(5000):
            fecha = fecha_base + timedelta(hours=i)
            hora = fecha.hour
            paradero_id = random.choices(
                population=[1,2,3,4,5,6,7,8,9,10],
                weights=[18,18,15,10,15,12,4,4,2,2],
                k=1
            )[0]
            recorrido_id = random.randint(1, 10)

            if 7 <= hora <= 9:
                flujo_pasajeros = random.randint(2500, 4000) if paradero_id in zonas_laborales else (random.randint(1200, 2500) if paradero_id in zonas_residenciales else random.randint(800, 1800))
            elif 17 <= hora <= 20:
                flujo_pasajeros = random.randint(2200, 3800) if paradero_id in zonas_laborales else (random.randint(1400, 2800) if paradero_id in zonas_residenciales else random.randint(800, 1800))
            else:
                flujo_pasajeros = random.randint(600, 1800) if paradero_id in zonas_laborales else random.randint(200, 1200)

            if recorrido_id >= 6:
                velocidad_promedio = max(30, 55 - (flujo_pasajeros / 250))
                tiempo_promedio_viaje = 15 + (flujo_pasajeros / 250) + random.uniform(-2, 2)
            else:
                velocidad_promedio = max(10, 40 - (flujo_pasajeros / 120))
                tiempo_promedio_viaje = 25 + (flujo_pasajeros / 60) + random.uniform(-5, 5)

            cur.execute("""
                INSERT INTO monitoreo_viajes (fecha_hora, paradero_id, recorrido_id, tiempo_promedio_viaje, flujo_pasajeros, velocidad_promedio)
                VALUES (%s,%s,%s,%s,%s,%s);
            """, (fecha, paradero_id, recorrido_id, round(tiempo_promedio_viaje, 2), flujo_pasajeros, round(velocidad_promedio, 2)))

    conn.commit()
    cur.close()
    conn.close()
    yield
    print("Apagando aplicación...")


app = FastAPI(
    title="API Movilidad Urbana RM",
    lifespan=lifespan
)

# =====================================================
# ESQUEMA DE ENTRADA ML (Pydantic)
# =====================================================
class PrediccionRequest(BaseModel):
    Comuna: str
    Tipo_dia: str
    Media_hora: str

# =====================================================
# ENDPOINT DE INFERENCIA DE MODELOS ML (POST)
# =====================================================
@app.post("/api/v1/predict")
def predecir_demanda(request: PrediccionRequest):
    logging.info(f"🔮 Petición de Inferencia: Comuna: {request.Comuna}, Tipo Día: {request.Tipo_dia}")
    
    try:
        if modelo_supervisado is not None and modelo_no_supervisado is not None:
            # Transformación numérica para el modelo
            comuna_idx = comuna_mapping.get(request.Comuna.upper(), 0)
            tipo_dia_idx = tipo_dia_mapping.get(request.Tipo_dia.upper(), 0)
            
            try:
                partes = request.Media_hora.split(":")
                hora_num = float(partes[0]) + (float(partes[1]) / 60.0)
            except Exception:
                hora_num = 12.0

            # Estructurar features para Scikit-Learn
            features = [[comuna_idx, hora_num, tipo_dia_idx]]
            
            # Ejecutar modelos
            pred_subidas = modelo_supervisado.predict(features)[0]
            pred_cluster = modelo_no_supervisado.predict(features)[0]
            
            subidas_estimadas = float(max(0.0, pred_subidas))
            cluster_asignado = int(pred_cluster)
            metodo = "Modelo_Produccion_ML"
        else:
            # Fallback en caso de que no carguen los archivos pkl
            es_hora_punta = request.Media_hora in ["07:30:00", "08:00:00", "18:00:00", "18:30:00"]
            subidas_estimadas = 92.4 if es_hora_punta else 18.3
            cluster_asignado = 3 if subidas_estimadas > 50 else 1
            metodo = "Simulador_EFT_Fallback"

        return {
            "status": "success",
            "comuna": request.Comuna.upper(),
            "tipo_dia": request.Tipo_dia.upper(),
            "bloque_horario": request.Media_hora,
            "subidas_promedio_estimadas": round(subidas_estimadas, 1),
            "cluster_comportamiento": cluster_asignado,
            "metodo_calculo": metodo
        }
    except Exception as e:
        logging.critical(f"Error en motor de predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error en inferencia de modelos: {str(e)}")


# =====================================================
# RESTO DE ENDPOINTS DE LA API (GETS)
# =====================================================
@app.get("/api/paraderos")
def obtener_paraderos():

    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            codigo,
            latitud,
            longitud,
            comuna_id
        FROM paraderos
        ORDER BY id;
    """)

    records = cur.fetchall()

    cur.close()
    conn.close()

    lista_paraderos = [
        {
            "id": r[0],
            "codigo": r[1],
            "latitud": float(r[2]),
            "longitud": float(r[3]),
            "comuna_id": r[4]
        }
        for r in records
    ]

    return lista_paraderos


# =====================================================
# RECORRIDOS
# =====================================================

@app.get("/api/recorridos")
def obtener_recorridos():

    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            nombre,
            empresa_operadora,
            capacidad_pasajeros
        FROM recorridos
        ORDER BY nombre;
    """)

    records = cur.fetchall()

    cur.close()
    conn.close()

    lista_recorridos = [
        {
            "id": r[0],
            "nombre": r[1],
            "empresa_operadora": r[2],
            "capacidad_pasajeros": r[3]
        }
        for r in records
    ]

    return lista_recorridos


# =====================================================
# MONITOREO DE VIAJES
# =====================================================

@app.get("/api/monitoreo")
def obtener_monitoreo():

    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            fecha_hora,
            paradero_id,
            recorrido_id,
            tiempo_promedio_viaje,
            flujo_pasajeros,
            velocidad_promedio
        FROM monitoreo_viajes
        ORDER BY fecha_hora;
    """)

    records = cur.fetchall()

    cur.close()
    conn.close()

    lista_monitoreo = [
        {
            "id": r[0],
            "fecha_hora": str(r[1]),
            "paradero_id": r[2],
            "recorrido_id": r[3],
            "tiempo_promedio_viaje": float(r[4]),
            "flujo_pasajeros": r[5],
            "velocidad_promedio": float(r[6])
        }
        for r in records
    ]

    return lista_monitoreo



@app.get("/")
def home():
    return {
        "mensaje": "API Movilidad Urbana RM funcionando - Docker y FastAPI"
    }


# # =====================================================
# # PREDICCIÓN ML
# # =====================================================
# @app.post("/api/predict")
# def predict(request: PredictionRequest):
#     try:

#         df = pd.DataFrame([request.model_dump()])

#         # Mantener el mismo orden usado durante el entrenamiento
#         df = df[
#             [
#                 "comuna_id",
#                 "comuna",
#                 "ingreso_promedio_hogar",
#                 "paradero_id",
#                 "latitud",
#                 "longitud",
#                 "recorrido_id",
#                 "recorrido",
#                 "empresa_operadora",
#                 "capacidad_pasajeros",
#                 "flujo_pasajeros",
#                 "velocidad_promedio",
#                 "hora",
#                 "dia",
#                 "mes"
#             ]
#         ]

#         resultado = predecir(df)

#         return {
#             "status": "success",
#             "prediccion": round(float(resultado[0]), 2),
#             "unidad": "minutos"
#         }

#     except Exception as e:
#         raise HTTPException(
#             status_code=500,
#             detail=f"Error al generar la predicción: {str(e)}"
#         )

@app.get("/api/analiticas")
def obtener_analiticas():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("""
        SELECT m.id, m.fecha_hora, c.id, c.nombre, c.ingreso_promedio_hogar, p.id, p.codigo, p.latitud, p.longitud,
               r.id, r.nombre, r.empresa_operadora, r.capacidad_pasajeros, m.tiempo_promedio_viaje, m.flujo_pasajeros, m.velocidad_promedio
        FROM monitoreo_viajes m
        JOIN paraderos p ON p.id = m.paradero_id
        JOIN comunas c ON c.id = p.comuna_id
        JOIN recorridos r ON r.id = m.recorrido_id
        ORDER BY m.fecha_hora;
    """)
    records = cur.fetchall()
    cur.close()
    conn.close()
    return [
        {
            "id": r[0], "fecha_hora": str(r[1]), "comuna_id": r[2], "comuna": r[3], "ingreso_promedio_hogar": float(r[4]),
            "paradero_id": r[5], "codigo_paradero": r[6], "latitud": float(r[7]), "longitud": float(r[8]),
            "recorrido_id": r[9], "recorrido": r[10], "empresa_operadora": r[11], "capacidad_pasajeros": r[12],
            "tiempo_promedio_viaje": float(r[13]), "flujo_pasajeros": r[14], "velocidad_promedio": float(r[15])
        } for r in records
    ]

@app.get("/api/comunas")
def obtener_comunas():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, ingreso_promedio_hogar FROM comunas ORDER BY nombre;")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "ingreso_promedio_hogar": float(r[2])} for r in records]

@app.get("/api/paraderos")
def obtener_paraderos():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT id, codigo, latitud, longitud, comuna_id FROM paraderos ORDER BY id;")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "codigo": r[1], "latitud": float(r[2]), "longitud": float(r[3]), "comuna_id": r[4]} for r in records]

@app.get("/api/recorridos")
def obtener_recorridos():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, empresa_operadora, capacidad_pasajeros FROM recorridos ORDER BY nombre;")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "nombre": r[1], "empresa_operadora": r[2], "capacidad_pasajeros": r[3]} for r in records]

@app.get("/api/monitoreo")
def obtener_monitoreo():
    conn = conectar_bd()
    cur = conn.cursor()
    cur.execute("SELECT id, fecha_hora, paradero_id, recorrido_id, tiempo_promedio_viaje, flujo_pasajeros, velocidad_promedio FROM monitoreo_viajes ORDER BY fecha_hora;")
    records = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": r[0], "fecha_hora": str(r[1]), "paradero_id": r[2], "recorrido_id": r[3], "tiempo_promedio_viaje": float(r[4]), "flujo_pasajeros": r[5], "velocidad_promedio": float(r[6])} for r in records]

@app.get("/data")
def get_data():
    contenido, click_status = cargar_datos()
    return contenido

# =============================================================================
# Configuración de la Interfaz del Dashboard (Streamlit)
# =============================================================================
st.set_page_config(
    page_title="Dashboard de Movilidad RM",
    page_icon="🚌",
    layout="wide"
)

st.title("🚌 Sistema de Optimización de Demanda - Red Movilidad")
st.markdown("---")

# 🟢 CONFIGURACIÓN CORREGIDA: Apunta a la API REST en el puerto 8000
#API_URL = "http://127.0.0.1:8000/api/v1/predict"
API_URL = "http://api:5000/api/v1/predict"
# =============================================================================
# Selectores de la Barra Lateral (Filtros)
# =============================================================================
st.sidebar.header("Filtros de Predicción")

comuna = st.sidebar.selectbox(
    "Selecciona la Comuna:",
    ["SANTIAGO", "PROVIDENCIA", "LAS CONDES", "MAIPU", "FLORIDA"]
)

tipo_dia = st.sidebar.selectbox(
    "Tipo de Día:",
    ["LABORAL", "SABADO", "DOMINGO"]
)

bloque_horario = st.sidebar.selectbox(
    "Bloque Horario (Media Hora):",
    ["07:00:00", "07:30:00", "08:00:00", "08:30:00", "09:00:00", 
     "12:00:00", "14:00:00", "18:00:00", "18:30:00", "19:00:00", "20:00:00"]
)

# =============================================================================
# Ejecución de la Predicción al hacer Click
# =============================================================================
if st.sidebar.button("Calcular Predicción de Demanda 🚀"):
    
    # Payload con la estructura exacta que espera el Pydantic de la API
    payload = {
        "Comuna": comuna,
        "Tipo_dia": tipo_dia,
        "Media_hora": bloque_horario
    }
    
    st.subheader(f"📊 Resultados de Análisis para {comuna}")
    
    try:
        # Realizar la petición POST al contenedor de la API
        response = requests.post(API_URL, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            
            # Crear las tarjetas visuales de los KPI
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    label="Subidas Estimadas Promedio", 
                    value=f"{data['subidas_promedio_estimadas']} pas."
                )
            
            with col2:
                st.metric(
                    label="Cluster de Comportamiento", 
                    value=f"Grupo {data['cluster_comportamiento']}"
                )
                
            with col3:
                st.metric(
                    label="Método de Cálculo Utilizado", 
                    value=data['metodo_calculo']
                )
            
            st.success("✨ ¡Datos obtenidos exitosamente de la API REST!")
            
            # Mostrar la respuesta cruda en un bloque organizado
            with st.expander("Ver respuesta detallada en formato JSON"):
                st.json(data)
                
        else:
            st.error(f"❌ La API respondió con código de error {response.status_code}")
            st.warning(response.text)
            
    except requests.exceptions.ConnectionError:
        st.error(f"🚨 No se pudo conectar con la API REST en la URL: {API_URL}")
        st.info("Asegúrate de que el contenedor de la API esté corriendo y respondiendo en el puerto 8000.")
        
    except Exception as e:
        st.error(f"💥 Ocurrió un error inesperado al realizar la consulta: {str(e)}")

else:
    st.info("💡 Modifica los filtros en la barra lateral izquierda y haz clic en **Calcular Predicción de Demanda** para procesar los datos de los modelos.")