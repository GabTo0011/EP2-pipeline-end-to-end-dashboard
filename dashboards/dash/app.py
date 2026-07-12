import streamlit as st
import requests
import pandas as pd
import altair as alt

# Configuración de la página del Dashboard
st.set_page_config(
    page_title="Control de Mando - Red Movilidad",
    page_icon="🚌",
    layout="wide"
)

API_URL = "http://127.0.0.1:8001/api/v1/predict"

st.title("🚌 Sistema de Optimización de Flotas - MTT")
st.markdown("---")

# --- BARRA LATERAL (Filtros de Entrada para la API) ---
st.sidebar.header("🎛️ Parámetros de Simulación")

comuna_input = st.sidebar.text_input("Comuna (Ej: SANTIAGO, MAIPU, PUENTE ALTO)", "SANTIAGO").upper().strip()
tipo_dia_input = st.sidebar.selectbox("Tipo de Día", ["LABORAL", "SABADO", "DOMINGO"])
media_hora_input = st.sidebar.selectbox(
    "Bloque Horario (Media Hora)",
    ["06:00:00", "07:30:00", "08:00:00", "12:00:00", "14:00:00", "18:00:00", "18:30:00", "21:00:00"]
)

# Petición automática a la API REST para obtener los datos predictivos
payload = {
    "Comuna": comuna_input,
    "Tipo_dia": tipo_dia_input,
    "Media_hora": media_hora_input
}

try:
    response = requests.post(API_URL, json=payload)
    if response.status_code == 200:
        api_data = response.json()
        subidas_predichas = api_data["subidas_promedio_estimadas"]
        cluster = api_data["cluster_comportamiento"]
    else:
        st.error(f"Error en la API REST: {response.status_code}")
        subidas_predichas, cluster = 0, 0
except Exception as e:
    st.error(f"No se pudo conectar con la API REST en el puerto 8000: {e}")
    subidas_predichas, cluster = 0, 0

# --- ESTRUCTURA DE PESTAÑAS  ---
tab1, tab2 = st.tabs(["📊 Pestaña Ejecutiva (Directivos MTT)", "⚙️ Pestaña Operativa (Planificadores Técnicos)"])

# 1. PESTAÑA EJECUTIVA (Métricas Macroeconómicas y Alertas)

with tab1:
    st.subheader("📈 Resumen de Carga y Alertas Estratégicas")
    
    # KPIs Claves de Negocio traducidos a impacto operativo/dinero
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(label="Pasajeros Estimados (Media Hora)", value=f"{subidas_predichas} subidas")
    with col2:
        # Lógica de negocio: si supera los 50 pasajeros por media hora, hay riesgo de aglomeración
        estado_alerta = "CRÍTICA" if subidas_predichas > 50 else "NORMAL"
        st.metric(label="Estado del Paradero", value=estado_alerta, delta="Monitorear Flota" if estado_alerta == "CRÍTICA" else "Estable")
    with col3:
        # Traduciendo el error o ineficiencia a pérdida económica estimada por bus mal asignado
        perdida_estimada = "$145.000" if subidas_predichas > 50 else "$0"
        st.metric(label="Costo de Ineficiencia Operacional (Est.)", value=perdida_estimada, delta="Por retraso de frecuencia", delta_color="inverse")

    st.markdown("### 🚨 Comunas con Mayor Riesgo de Congestión Esperada")
    # Gráfico simulado macro para toma de decisiones rápidas
    data_macro = pd.DataFrame({
        'Comuna': ['SANTIAGO', 'MAIPU', 'PUENTE ALTO', 'FLORIDA', 'PROVIDENCIA'],
        'Subidas Esperadas (Hora Punta)': [92.4, 85.1, 78.3, 64.0, 55.2]
    })
    
    chart_macro = alt.Chart(data_macro).mark_bar(color='#ff4b4b').encode(
        x='Subidas Esperadas (Hora Punta):Q',
        y=alt.Y('Comuna:N', sort='-x')
    ).properties(height=300)
    
    st.altair_chart(chart_macro, use_container_width=True)
    
# 2. PESTAÑA OPERATIVA (Análisis Técnico de Clusters del Modelo No Supervisado)

with tab2:
    st.subheader("🔬 Segmentación de Paraderos y Curvas de Carga")
    st.caption("Esta pestaña despliega el comportamiento técnico de los grupos/clusters identificados por el modelo K-Means.")
    
    col_op1, col_op2 = st.columns([1, 2])
    
    with col_op1:
        st.info(f"**Análisis del Bloque Actual:**\n\nEl paradero seleccionado pertenece al **Cluster {cluster}**.")
        if cluster == 3:
            st.warning("⚠️ **Perfil del Cluster 3:** Alta densidad laboral en hora punta. Requiere inyección prioritaria de buses vacíos desde cabecera.")
        else:
            st.success("✅ **Perfil del Cluster 1:** Flujo residencial controlado. Frecuencias estándar asignadas de forma óptima.")
            
    with col_op2:
        # Gráfico de dispersión/curva horaria de los clusters
        st.markdown("**Comportamiento de Carga por Bloque Horario y Cluster**")
        data_clusters = pd.DataFrame({
            'Media Hora': ["06:00", "07:30", "08:00", "12:00", "14:00", "18:00", "18:30", "21:00"] * 2,
            'Subidas Promedio': [10, 85, 92, 20, 25, 88, 90, 30,  5, 15, 20, 12, 15, 14, 12, 8],
            'Cluster': ['Cluster 3 (Alta Demanda)'] * 8 + ['Cluster 1 (Residencial Valle)'] * 8
        })
        
        chart_op = alt.Chart(data_clusters).mark_line(point=True).encode(
            x='Media Hora:N',
            y='Subidas Promedio:Q',
            color='Cluster:N'
        ).properties(height=280)
        
        st.altair_chart(chart_op, use_container_width=True)