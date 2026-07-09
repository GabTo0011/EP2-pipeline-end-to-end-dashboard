import os
import pandas as pd
import requests

# 1. Usar variables de entorno con fallback para mantener compatibilidad local
API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:5000/api")
OUTPUT_DIR = os.getenv("OUTPUT_DIR", ".")

# 2. Construir URLs dinámicamente
URL_COMUNAS = f"{API_BASE_URL}/comunas"
URL_PARADEROS = f"{API_BASE_URL}/paraderos"
URL_RECORRIDOS = f"{API_BASE_URL}/recorridos"
URL_MONITOREO = f"{API_BASE_URL}/monitoreo"
URL_ANALITICAS = f"{API_BASE_URL}/analiticas"

def extraer_datos(url):
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()

def guardar_csv(datos, nombre_archivo):
    df = pd.DataFrame(datos)
    # 3. Guardar en el directorio de salida especificado
    ruta_completa = os.path.join(OUTPUT_DIR, nombre_archivo)
    df.to_csv(ruta_completa, index=False, encoding="utf-8")
    print(f"{ruta_completa} generado")

def ejecutar_pipeline():
    # Asegurar que el directorio de salida exista
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        print("Extrayendo comunas...")
        guardar_csv(extraer_datos(URL_COMUNAS), "comunas.csv")
        print("Extrayendo paraderos...")
        guardar_csv(extraer_datos(URL_PARADEROS), "paraderos.csv")
        print("Extrayendo recorridos...")
        guardar_csv(extraer_datos(URL_RECORRIDOS), "recorridos.csv")
        print("Extrayendo monitoreo...")
        guardar_csv(extraer_datos(URL_MONITOREO), "monitoreo_viajes.csv")
        print("Extrayendo dataset consolidado...")
        guardar_csv(extraer_datos(URL_ANALITICAS), "dataset_movilidad_rm.csv")
        print("ETL finalizado correctamente")

    except Exception as e:
        print(f"Error en ETL: {e}")
        raise e # Es importante relanzar el error para que Docker sepa si falló

if __name__ == "__main__":
    ejecutar_pipeline()