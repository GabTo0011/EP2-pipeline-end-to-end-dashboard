import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Movilidad - RM",
    page_icon="🚌",
    layout="wide",
)

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos():
    """Carga el dataset consolidado de movilidad."""
    # La ruta es relativa a la ubicación del script del dashboard
    # Se asume que el script está en la carpeta /etl y los datos en /data/raw
    ruta_dataset = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'dataset_movilidad_rm.csv')
    try:
        df = pd.read_csv(ruta_dataset)
        return df
    except FileNotFoundError:
        st.error(f"El archivo no se encontró en la ruta: {ruta_dataset}")
        st.info("Asegúrate de que el pipeline ETL se haya ejecutado y que la ruta al archivo CSV sea correcta.")
        return None

df = cargar_datos()

if df is not None:
    st.title("🚌 Dashboard de Movilidad en la Región Metropolitana")

    # --- BARRA LATERAL PARA SELECCIÓN DE AUDIENCIA ---
    st.sidebar.title("Selección de Audiencia")
    audiencia = st.sidebar.radio(
        "Elige tu perfil:",
        ("Ejecutivo", "Técnico", "Operativo")
    )

    # --- VISTA PARA CADA AUDIENCIA ---
    if audiencia == "Ejecutivo":
        st.header("Resumen Ejecutivo")
        st.markdown("""
        Esta vista presenta los indicadores clave (KPIs) del sistema de transporte para la toma de decisiones estratégicas.
        """)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total de Viajes Monitoreados", f"{df.shape[0]:,}")
        col2.metric("Velocidad Promedio", f"{df['velocidad_promedio'].mean():.2f} km/h")
        col3.metric("Comuna más Frecuente", df['comuna'].mode()[0])

        st.subheader("Distribución de Viajes por Comuna de Origen")
        fig_comunas = px.bar(
            df['comuna'].value_counts().nlargest(10),
            title="Top 10 Comunas con más Viajes",
            labels={'value': 'Número de Viajes', 'index': 'Comuna'}
        )
        st.plotly_chart(fig_comunas, use_container_width=True)

        st.subheader("Flujo de Pasajeros por Hora")
        df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
        flujo_por_hora = df.groupby(df['fecha_hora'].dt.hour)['flujo_pasajeros'].sum()
        fig_comunas = px.line(
            x=flujo_por_hora.index,
            y=flujo_por_hora.values,
            title="Flujo de Pasajeros total por Hora del Día",
            labels={'x': 'Hora del Día', 'y': 'Total Flujo Pasajeros'},
            markers=True
        )
        st.plotly_chart(fig_comunas, use_container_width=True)

    elif audiencia == "Técnico":
        st.header("Análisis Técnico del Sistema")
        st.markdown("""
        Esta vista ofrece una exploración detallada de la calidad de los datos y la estructura del dataset.
        """)

        st.subheader("Vista Previa del Dataset Consolidado")
        st.dataframe(df.head())

        st.subheader("Estadísticas Descriptivas")
        st.dataframe(df.describe())

        st.subheader("Valores Nulos en el Dataset")
        st.dataframe(df.isnull().sum().to_frame('Valores Nulos'))

    elif audiencia == "Operativo":
        st.header("Monitor Operacional")
        st.markdown("""
        Esta vista permite supervisar el estado de los recorridos y paraderos para la gestión diaria.
        """)

        # Filtro por recorrido
        recorrido_seleccionado = st.selectbox(
            "Selecciona un Recorrido para analizar:",
            df['recorrido'].unique()
        )

        df_filtrado = df[df['recorrido'] == recorrido_seleccionado]

        st.subheader(f"Detalle de Viajes para el Recorrido: {recorrido_seleccionado}")
        st.dataframe(df_filtrado)

        st.subheader("Mapa de Paraderos del Recorrido")
        # Asumiendo columnas de latitud y longitud
        if 'latitud' in df_filtrado.columns and 'longitud' in df_filtrado.columns:
            map_data = df_filtrado[['latitud', 'longitud']].dropna().copy()
            map_data.rename(columns={'latitud': 'lat', 'longitud': 'lon'}, inplace=True)
            st.map(map_data)
        else:
            st.warning("No se encontraron datos de geolocalización (latitud, longitud) para el mapa.")

else:
    st.warning("No se pudieron cargar los datos para el dashboard.")