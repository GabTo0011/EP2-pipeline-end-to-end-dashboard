import os
import sys
import subprocess

import random
from datetime import datetime, timedelta


if sys.platform == 'win32':
    try:
        subprocess.run(
            ["chcp", "65001"],
            shell=True,
            check=True,
            stdout=subprocess.DEVNULL
        )

        import ctypes
        ctypes.windll.kernel32.SetConsoleCP(65001)
        ctypes.windll.kernel32.SetConsoleOutputCP(65001)

    except Exception:
        pass

from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import psycopg2


def conectar_bd():
    try:
        return psycopg2.connect(
            host="127.0.0.1",
            database="movilidad_rm_db",
            user="estudiante",
            password="estudiante_password",
            port=5433,
            client_encoding='utf8'
        )
    except Exception as e:
        print("\n" + "="*50)
        print("¡ERROR DE POSTGRESQL DETECTADO!")
        print(repr(e))
        print("="*50 + "\n")
        raise e


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Iniciando aplicación y conectando a PostgreSQL...")

    try:
        conn = conectar_bd()

    except Exception as e:

        print("\n" + "=" * 60)
        print("[ERROR CRITICO DE CONEXION]")
        error_msg = str(e).encode(
            'utf8',
            errors='ignore'
        ).decode('utf8')

        print(error_msg)
        print("=" * 60 + "\n")

        os._exit(1)

    cur = conn.cursor()

    # =====================================================
    # TABLA COMUNAS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS comunas(
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100),
            ingreso_promedio_hogar NUMERIC(12,2)
        );
    """)

    # =====================================================
    # TABLA PARADEROS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS paraderos(
            id SERIAL PRIMARY KEY,
            codigo VARCHAR(20),
            latitud DECIMAL(10,7),
            longitud DECIMAL(10,7),
            comuna_id INTEGER REFERENCES comunas(id)
        );
    """)

    # =====================================================
    # TABLA RECORRIDOS
    # =====================================================

    cur.execute("""
        CREATE TABLE IF NOT EXISTS recorridos(
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(50),
            empresa_operadora VARCHAR(100),
            capacidad_pasajeros INTEGER
        );
    """)

    # =====================================================
    # TABLA MONITOREO_VIAJES
    # =====================================================

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

    # =====================================================
    # DATOS DE PRUEBA
    # =====================================================

    cur.execute("SELECT COUNT(*) FROM comunas;")
    resultado = cur.fetchone()

    if resultado and resultado[0] == 0:


        # ==========================
        # COMUNAS
        # ==========================

        cur.execute("""
            INSERT INTO comunas
            (nombre, ingreso_promedio_hogar)
            VALUES
            ('Puente Alto',850000),
            ('Maipu',950000),
            ('San Bernardo',800000),
            ('Pudahuel',900000),
            ('La Florida',1100000),
            ('Santiago',1400000),
            ('Providencia',2200000),
            ('Las Condes',3000000),
            ('Vitacura',3800000),
            ('Lo Barnechea',4200000);
        """)

        # ==========================
        # PARADEROS
        # ==========================

        cur.execute("""
            INSERT INTO paraderos
            (codigo, latitud, longitud, comuna_id)
            VALUES
            ('PA101',-33.6111,-70.5755,1),
            ('MA102',-33.5100,-70.7600,2),
            ('SB103',-33.5900,-70.7000,3),
            ('PD104',-33.4400,-70.7400,4),
            ('LF105',-33.5200,-70.5800,5),
            ('ST106',-33.4500,-70.6667,6),
            ('PR107',-33.4300,-70.6100,7),
            ('LC108',-33.4100,-70.5600,8),
            ('VT109',-33.3900,-70.5700,9),
            ('LB110',-33.3500,-70.5200,10);
        """)

        # ==========================
        # RECORRIDOS
        # ==========================

        cur.execute("""
            INSERT INTO recorridos
            (nombre, empresa_operadora, capacidad_pasajeros)
            VALUES
            ('210','Metbus',120),
            ('405','STP',100),
            ('506','Redbus',110),
            ('301','Vule',115),
            ('712','Metbus',120),
            ('Metro L1','Metro',1000),
            ('Metro L4','Metro',1000),
            ('Metro L5','Metro',1000),
            ('Metro L6','Metro',1000),
            ('Metro L3','Metro',1000);
        """)

        # ==========================
        # DATOS HISTORICOS
        # ==========================

        fecha_base = datetime(2025, 1, 1, 0, 0)

        # Santiago, Providencia y Las Condes
        zonas_laborales = [6, 7, 8, 9]

        # Comunas dormitorio
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

            # Hora punta mañana
            if 7 <= hora <= 9:

                if paradero_id in zonas_laborales:
                    flujo_pasajeros = random.randint(2500, 4000)

                elif paradero_id in zonas_residenciales:
                    flujo_pasajeros = random.randint(1200, 2500)

                else:
                    flujo_pasajeros = random.randint(800, 1800)

            # Hora punta tarde
            elif 17 <= hora <= 20:

                if paradero_id in zonas_laborales:
                    flujo_pasajeros = random.randint(2200, 3800)

                elif paradero_id in zonas_residenciales:
                    flujo_pasajeros = random.randint(1400, 2800)

                else:
                    flujo_pasajeros = random.randint(800, 1800)

            # Horario normal
            else:

                if paradero_id in zonas_laborales:
                    flujo_pasajeros = random.randint(600, 1800)
                else:
                    flujo_pasajeros = random.randint(200, 1200)

            # Metro
            if recorrido_id >= 6:

                velocidad_promedio = max(
                    30,
                    55 - (flujo_pasajeros / 250)
                )

                tiempo_promedio_viaje = (
                    15 +
                    (flujo_pasajeros / 250)
                    + random.uniform(-2, 2)
                )

            # Bus
            else:

                velocidad_promedio = max(
                    10,
                    40 - (flujo_pasajeros / 120)
                )

                tiempo_promedio_viaje = (
                    25 +
                    (flujo_pasajeros / 60)
                    + random.uniform(-5, 5)
                )

            velocidad_promedio = round(
                velocidad_promedio,
                2
            )

            tiempo_promedio_viaje = round(
                tiempo_promedio_viaje,
                2
            )

            cur.execute("""
                INSERT INTO monitoreo_viajes
                (
                    fecha_hora,
                    paradero_id,
                    recorrido_id,
                    tiempo_promedio_viaje,
                    flujo_pasajeros,
                    velocidad_promedio
                )
                VALUES (%s,%s,%s,%s,%s,%s);
            """,
            (
                fecha,
                paradero_id,
                recorrido_id,
                tiempo_promedio_viaje,
                flujo_pasajeros,
                velocidad_promedio
            ))

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
# GET TODAS LAS ANALITICAS
# =====================================================

@app.get("/api/analiticas")
def obtener_analiticas():

    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            m.id,
            m.fecha_hora,

            c.id AS comuna_id,
            c.nombre AS comuna,
            c.ingreso_promedio_hogar,

            p.id AS paradero_id,
            p.codigo AS codigo_paradero,
            p.latitud,
            p.longitud,

            r.id AS recorrido_id,
            r.nombre AS recorrido,
            r.empresa_operadora,
            r.capacidad_pasajeros,

            m.tiempo_promedio_viaje,
            m.flujo_pasajeros,
            m.velocidad_promedio

        FROM monitoreo_viajes m

        JOIN paraderos p
            ON p.id = m.paradero_id

        JOIN comunas c
            ON c.id = p.comuna_id

        JOIN recorridos r
            ON r.id = m.recorrido_id

        ORDER BY m.fecha_hora;
    """)

    records = cur.fetchall()

    cur.close()
    conn.close()

    lista_analiticas = [
        {
            "id": r[0],
            "fecha_hora": str(r[1]),

            "comuna_id": r[2],
            "comuna": r[3],
            "ingreso_promedio_hogar": float(r[4]),

            "paradero_id": r[5],
            "codigo_paradero": r[6],
            "latitud": float(r[7]),
            "longitud": float(r[8]),

            "recorrido_id": r[9],
            "recorrido": r[10],
            "empresa_operadora": r[11],
            "capacidad_pasajeros": r[12],

            "tiempo_promedio_viaje": float(r[13]),
            "flujo_pasajeros": r[14],
            "velocidad_promedio": float(r[15])
        }
        for r in records
    ]

    return lista_analiticas

# =====================================================
# COMUNAS
# =====================================================

@app.get("/api/comunas")
def obtener_comunas():

    conn = conectar_bd()
    cur = conn.cursor()

    cur.execute("""
        SELECT
            id,
            nombre,
            ingreso_promedio_hogar
        FROM comunas
        ORDER BY nombre;
    """)

    records = cur.fetchall()

    cur.close()
    conn.close()

    lista_comunas = [
        {
            "id": r[0],
            "nombre": r[1],
            "ingreso_promedio_hogar": float(r[2])
        }
        for r in records
    ]

    return lista_comunas


# =====================================================
# PARADEROS
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
        "mensaje": "API Movilidad Urbana RM funcionando"
    }