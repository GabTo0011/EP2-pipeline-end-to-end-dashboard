import streamlit as st
import pandas as pd
import os

@st.cache_data
def cargar_datos():
    """Carga el dataset consolidado de movilidad."""
    # La ruta es relativa al WORKDIR del contenedor (/app) y el volumen mapeado
    ruta_dataset = os.path.join('data', 'raw', 'dataset_movilidad_rm.csv')
    try:
        df = pd.read_csv(ruta_dataset)
        # Convertir la columna de fecha/hora aquí para asegurar que siempre tenga el tipo correcto
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
        return df
    except FileNotFoundError:
        st.error(f"El archivo no se encontró en la ruta: {ruta_dataset}")
        st.info("Asegúrate de que el pipeline ETL se haya ejecutado y que la ruta al archivo CSV sea correcta.")
        return None