import streamlit as st
import requests
import pandas as pd

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