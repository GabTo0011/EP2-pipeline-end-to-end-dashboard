import os
import pickle
import logging
import pandas as pd  
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# Configuración del Logging solicitado
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("api_server.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

app = FastAPI(
    title="API de Optimización de Demanda - Red Movilidad (MTT)",
    description="API REST funcional para la predicción y segmentación de subidas de pasajeros por bloques horarios.",
    version="1.0.0"
)

# 1. Definición del Esquema de Entrada utilizando Pydantic
class PrediccionRequest(BaseModel):
    Comuna: str
    Tipo_dia: str
    Media_hora: str

# 2. Variables globales para los modelos
modelo_supervisado = None
modelo_no_supervisado = None

@app.on_event("startup")
def cargar_modelos():
    """
    Carga los modelos entrenados al iniciar la API de forma segura.
    """
    global modelo_supervisado, modelo_no_supervisado
    
    ruta_sup = "models/modelo_regresion.pkl"
    ruta_no_sup = "models/modelo_kmeans.pkl"
    
    logging.info("Iniciando servicio y verificando artefactos de Machine Learning...")
    
    if os.path.exists(ruta_sup) and os.path.exists(ruta_no_sup):
        try:
            with open(ruta_sup, "rb") as f:
                modelo_supervisado = pickle.load(f)
            with open(ruta_no_sup, "rb") as f:
                modelo_no_supervisado = pickle.load(f)
            logging.info("Modelos de Machine Learning cargados exitosamente desde la carpeta /models/")
        except Exception as e:
            logging.error(f"Error al deserializar los archivos de modelos: {str(e)}")
    else:
        logging.warning("Los archivos .pkl no se encuentran en /models/. Se activará el modo de simulación temporal.")

# Diccionarios de mapeo rápido para convertir texto a números (Label Encoding básico)
comuna_mapping = {"SANTIAGO": 0, "PROVIDENCIA": 1, "LAS CONDES": 2, "MAIPU": 3, "FLORIDA": 4}
tipo_dia_mapping = {"LABORAL": 0, "SABADO": 1, "DOMINGO": 2}

def transformar_entrada(request: PrediccionRequest):
    """Convierte los textos de la petición en características numéricas para el modelo"""
    # Convertimos a mayúsculas para evitar errores de tipeo
    comuna_idx = comuna_mapping.get(request.Comuna.upper(), 0) 
    tipo_dia_idx = tipo_dia_mapping.get(request.Tipo_dia.upper(), 0)
    
    # Extraemos la hora como un número flotante (ej: "07:30:00" -> 7.5)
    try:
        partes = request.Media_hora.split(":")
        hora_num = float(partes[0]) + (float(partes[1]) / 60.0)
    except:
        hora_num = 12.0 # Valor por defecto si el formato falla
        
    # El modelo fue entrenado con 3 características (features)
    return pd.DataFrame([[comuna_idx, hora_num, tipo_dia_idx]], columns=['feature_1', 'feature_2', 'feature_3'])

# 3. Endpoints de la API REST 
@app.get("/")
def home():
    return {
        "status": "Operativa",
        "proyecto": "EFT - Programación para la Ciencia de Datos",
        "caso": "Matrices de Viajes MTT 2026"
    }

@app.post("/api/v1/predict")
def predecir_demanda(request: PrediccionRequest):
    """
    Endpoint principal para predecir la afluencia de pasajeros en un paradero/comuna.
    Devuelve la estimación utilizando los modelos cargados en memoria.
    """
    logging.info(f"Petición recibida para Comuna: {request.Comuna}, Horario: {request.Media_hora}")
    
    if not request.Comuna.strip() or not request.Media_hora.strip():
        logging.error("Petición rechazada: Campos obligatorios vacíos.")
        raise HTTPException(status_code=400, detail="La comuna y la media hora no pueden estar vacías.")

    try:
        if modelo_supervisado is not None and modelo_no_supervisado is not None:
            # --- PREDICCIÓN REAL ---
            # 1. Transformamos los datos de entrada
            features = transformar_entrada(request)
            
            # 2. Ejecutamos los modelos .predict() reales de Scikit-Learn
            pred_subidas = modelo_supervisado.predict(features)[0]
            pred_cluster = modelo_no_supervisado.predict(features)[0]
            
            # Evitamos que la regresión devuelva números negativos de subidas
            subidas_estimadas = max(0.0, float(pred_subidas))
            cluster_asignado = int(pred_cluster)
            metodo = "Modelo_Produccion_ML"
        else:
            # --- MODO SIMULACIÓN (FALLBACK) ---
            es_hora_punta = request.Media_hora in ["07:30:00", "08:00:00", "08:30:00", "18:00:00", "18:30:00", "19:00:00"]
            if request.Tipo_dia.upper() == "DOMINGO":
                subidas_estimadas = 14.5 if es_hora_punta else 4.2
                cluster_asignado = 1
            else:
                subidas_estimadas = 92.4 if es_hora_punta else 18.3
                cluster_asignado = 3
            metodo = "Simulador_EFT_Fallback"

        logging.info(f"Predicción calculada con éxito -> Subidas: {subidas_estimadas}, Cluster: {cluster_asignado}")
        
        return {
            "comuna": request.Comuna.upper(),
            "tipo_dia": request.Tipo_dia.upper(),
            "bloque_horario": request.Media_hora,
            "subidas_promedio_estimadas": round(subidas_estimadas, 1),
            "cluster_comportamiento": cluster_asignado,
            "metodo_calculo": metodo
        }

    except Exception as e:
        logging.critical(f"Error interno del servidor al procesar predicción: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error interno en el cálculo de la demanda: {str(e)}")