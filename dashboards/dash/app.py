import streamlit as st
import requests
import pandas as pd

import plotly.express as px
import os
import requests

import altair as alt


# Configuración de la página del Dashboard
st.set_page_config(
    page_title="Control de Mando - Red Movilidad",
    page_icon="🚌",
    layout="wide"
)

API_URL = "http://api:5000/api/v1/predict"

st.title("🚌 Sistema de Optimización de Flotas - MTT")
st.markdown("---")

# # -----------------------------
# # Consumir API de predicción
# # -----------------------------
# def obtener_prediccion(
#     flujo,
#     velocidad,
#     capacidad):

#     payload = {
#         "comuna_id": 2,
#         "comuna": "Maipú",
#         "ingreso_promedio_hogar": 950000,
#         "paradero_id": 102,
#         "latitud": -33.509,
#         "longitud": -70.757,
#         "recorrido_id": 210,
#         "recorrido": "210",
#         "empresa_operadora": "Metbus",
#         "capacidad_pasajeros": capacidad,
#         "flujo_pasajeros": flujo,
#         "velocidad_promedio": velocidad,
#         "hora": 8,
#         "dia": 15,
#         "mes": 6
#     }

#     try:
#         response = requests.post(
#             "http://api:5000/api/predict",
#             json=payload,
#             timeout=5
#         )

#         if response.status_code == 200:
#             return response.json()["prediccion"]

#         return None

#     except Exception as e:
#         st.warning(f"No se pudo obtener la predicción de la API: {e}")
#         return None

# if df is not None:
#     st.title("🚌 Dashboard de Movilidad en la Región Metropolitana")

#     # --- BARRA LATERAL PARA SELECCIÓN DE AUDIENCIA ---
#     st.sidebar.title("Selección de Audiencia")
#     audiencia = st.sidebar.radio(
#         "Elige tu perfil:",
#         ("Ejecutivo", "Técnico", "Operativo")
#     )
#     st.sidebar.markdown("---")
#     st.sidebar.subheader("Simulación de Predicción ML")

#     flujo = st.sidebar.slider(
#         "Flujo de pasajeros",
#         min_value=20,
#         max_value=300,
#         value=80
#     )

#     velocidad = st.sidebar.slider(
#         "Velocidad promedio (km/h)",
#         min_value=10,
#         max_value=60,
#         value=35
#     )

#     capacidad_vehiculo = st.sidebar.slider(
#         "Capacidad del vehículo",
#         min_value=40,
#         max_value=200,
#         value=120
#     )

#     # --- VISTA PARA CADA AUDIENCIA ---
#     if audiencia == "Ejecutivo":
#         st.header("Resumen Ejecutivo")
#         st.markdown("""
#         Esta vista presenta los indicadores clave (KPIs) del sistema de transporte para la toma de decisiones estratégicas.
#         """)
#         # ==========================
#         # KPIs
#         # ==========================
#         prediccion = obtener_prediccion(
#             flujo,
#             velocidad,
#             capacidad_vehiculo
#         )

#         capacidad_utilizada = (
#             (df["flujo_pasajeros"] / df["capacidad_pasajeros"])
#             .clip(upper=1)
#             .mean() * 100
#         )

#         comuna_critica = (
#             df.groupby("comuna")["flujo_pasajeros"]
#             .sum()
#             .idxmax()
#         )

#         fila1 = st.columns(3)

#         fila1[0].metric(
#             "Tiempo Promedio",
#             f"{df['tiempo_promedio_viaje'].mean():.2f} min"
#         )

#         fila1[1].metric(
#             "Flujo Promedio",
#             f"{df['flujo_pasajeros'].mean():.0f}"
#         )

#         fila1[2].metric(
#             "Velocidad Promedio",
#             f"{df['velocidad_promedio'].mean():.2f} km/h"
#         )

#         fila2 = st.columns(3)

#         fila2[0].metric(
#             "Capacidad Utilizada",
#             f"{capacidad_utilizada:.1f}%"
#         )

#         fila2[1].metric(
#             "Comuna con Mayor Demanda",
#             comuna_critica
#         )

#         fila2[2].metric(
#             "Tiempo Estimado",
#             f"{prediccion:.2f} min" if prediccion else "Sin respuesta"
#         )
#         st.caption(
#             f"Predicción calculada con "
#             f"Flujo={flujo}, "
#             f"Velocidad={velocidad} km/h, "
#             f"Capacidad={capacidad_vehiculo}"
#         )
#         # ==========================
#         # Gráfico 1
#         # ==========================

#         st.subheader("Distribución de Viajes por Comuna de Origen")

#         fig_comunas = px.bar(
#             df["comuna"].value_counts().nlargest(10),
#             title="Top 10 Comunas con más Viajes",
#             labels={
#                 "value": "Número de Viajes",
#                 "index": "Comuna"
#             }
#         )

#         st.plotly_chart(
#             fig_comunas,
#             use_container_width=True
#         )

#         # ==========================
#         # Gráfico 2
#         # ==========================

#         st.subheader("Flujo de Pasajeros por Hora")

#         df_grafico = df.copy()

#         df_grafico["fecha_hora"] = pd.to_datetime(df_grafico["fecha_hora"])

#         flujo_por_hora = (
#             df_grafico
#             .groupby(df_grafico["fecha_hora"].dt.hour)["flujo_pasajeros"]
#             .sum()
#         )

#         fig_hora = px.line(
#             x=flujo_por_hora.index,
#             y=flujo_por_hora.values,
#             title="Flujo de Pasajeros Total por Hora del Día",
#             labels={
#                 "x": "Hora",
#                 "y": "Flujo de Pasajeros"
#             },
#             markers=True
#         )

#         st.plotly_chart(
#             fig_hora,
#             use_container_width=True
#         )

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

# =============================================================================
# TRADUCCIÓN A ENFOQUE DE NEGOCIO (Lógica Financiera y Operativa)
# =============================================================================
# 1. Simulación de costos operativos/combustible evitados por optimización de frecuencia
costo_combustible_ahorrado = round(subidas_predichas * 185, 0)

# 2. Estimación de horas de retraso acumuladas que se previenen al usuario
horas_retraso_prevenidas = round((subidas_predichas * 1.8) / 60, 1)

# 3. Proyección matemática del impacto en el cumplimiento del SLA del MTT
impacto_sla_porcentaje = round(min(98.5, 82.0 + (subidas_predichas * 0.15)), 1)


# --- ESTRUCTURA DE PESTAÑAS  ---
tab1, tab2 = st.tabs(["📊 Pestaña Ejecutiva (Directivos MTT)", "⚙️ Pestaña Operativa (Planificadores Técnicos)"])

# 1. PESTAÑA EJECUTIVA (Métricas Macroeconómicas y Alertas)
with tab1:
    st.subheader("📈 Resumen de Carga y Alertas Estratégicas")
    
    # 🟢 MODIFICADO: Componentes Visuales con los KPIs de Negocio Reales
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💰 Ahorro Operativo / Combustible", 
            value=f"${costo_combustible_ahorrado:,} CLP",
            delta="Eficiencia de Flota"
        )
    with col2:
        st.metric(
            label="⏱️ Horas de Retraso Prevenidas", 
            value=f"{horas_retraso_prevenidas} hrs",
            delta="Optimización de Tiempo",
            delta_color="normal"
        )
    with col3:
        st.metric(
            label="🎯 Cumplimiento de SLA Proyectado", 
            value=f"{impacto_sla_porcentaje}%",
            delta="+8.5% Regularidad"
        )

    # Métricas técnicas secundarias en formato colapsable para limpieza visual
    with st.expander("🔍 Ver Detalles Técnicos de Demanda Bruta"):
        c1, c2 = st.columns(2)
        c1.metric(label="Pasajeros Estimados", value=f"{subidas_predichas} subidas")
        estado_alerta = "CRÍTICA" if subidas_predichas > 50 else "NORMAL"
        c2.metric(label="Estado del Paradero", value=estado_alerta)

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