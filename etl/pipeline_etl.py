import pandas as pd
import requests

URL_COMUNAS = "http://127.0.0.1:8000/api/comunas"
URL_PARADEROS = "http://127.0.0.1:8000/api/paraderos"
URL_RECORRIDOS = "http://127.0.0.1:8000/api/recorridos"
URL_MONITOREO = "http://127.0.0.1:8000/api/monitoreo"
URL_ANALITICAS = "http://127.0.0.1:8000/api/analiticas"


def extraer_datos(url):
    respuesta = requests.get(url)
    respuesta.raise_for_status()
    return respuesta.json()


def guardar_csv(datos, nombre_archivo):

    df = pd.DataFrame(datos)

    df.to_csv(
        nombre_archivo,
        index=False,
        encoding="utf-8"
    )

    print(f"{nombre_archivo} generado")


def ejecutar_pipeline():

    try:

        print("Extrayendo comunas...")
        guardar_csv(
            extraer_datos(URL_COMUNAS),
            "comunas.csv"
        )

        print("Extrayendo paraderos...")
        guardar_csv(
            extraer_datos(URL_PARADEROS),
            "paraderos.csv"
        )

        print("Extrayendo recorridos...")
        guardar_csv(
            extraer_datos(URL_RECORRIDOS),
            "recorridos.csv"
        )

        print("Extrayendo monitoreo...")
        guardar_csv(
            extraer_datos(URL_MONITOREO),
            "monitoreo_viajes.csv"
        )

        print("Extrayendo dataset consolidado...")
        guardar_csv(
            extraer_datos(URL_ANALITICAS),
            "dataset_movilidad_rm.csv"
        )

        print("ETL finalizado correctamente")

    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    ejecutar_pipeline()