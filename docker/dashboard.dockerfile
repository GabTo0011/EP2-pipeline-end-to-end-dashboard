# =============================================================================
# Dockerfile - Dashboard Streamlit (Movilidad RM)
# =============================================================================
# Imagen base: Python 3.11 slim (Debian, ligera y estable)
# Propósito: Ejecutar el dashboard interactivo Streamlit en un contenedor
# Puerto: 8501 (puerto estándar de Streamlit)
# =============================================================================

# 1. Imagen base con versión fija para reproducibilidad
FROM python:3.11-slim

# 2. Metadatos del contenedor (OCI estándar)
LABEL maintainer="equipo_dev@empresa.com"
LABEL org.opencontainers.image.title="Dashboard Movilidad RM"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="Dashboard Streamlit para visualización de movilidad en la Región Metropolitana"

# 3. Variables de entorno para optimización en contenedores
#    - PYTHONDONTWRITEBYTECODE: No genera .pyc (innecesarios en contenedor)
#    - PYTHONUNBUFFERED: Logs en tiempo real sin buffer
#    - STREAMLIT_SERVER_*: Configuración del servidor Streamlit para Docker
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
    STREAMLIT_SERVER_HEADLESS=true \
    STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

# 4. Establecer directorio de trabajo
WORKDIR /app

# 5. Instalar dependencias del sistema necesarias para compilación de paquetes
#    y herramienta curl para healthcheck. Limpiar cache apt en la misma capa.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# 6. Copiar SOLO requirements.txt primero (aprovecha caché de capas Docker)
COPY requirements.txt .

# 7. Instalar dependencias de Python
#    --no-cache-dir reduce el tamaño de la imagen final
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 8. Copiar el código fuente de la aplicación
#    El .dockerignore excluye archivos innecesarios del contexto
COPY . .

# 9. Crear usuario no-root por seguridad
#    Nunca ejecutar servicios como root en producción
RUN addgroup --system dashgroup && \
    adduser --system --ingroup dashgroup dashuser && \
    chown -R dashuser:dashgroup /app

USER dashuser

# 10. Exponer el puerto estándar de Streamlit
#     Documenta el puerto; el mapeo real se define en docker-compose.yml
EXPOSE 8501

# 11. Healthcheck para monitoreo del estado del servicio
#     Verifica que Streamlit responda en su endpoint de salud
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# 12. Comando de inicio: Streamlit en modo servidor headless
#     - dash/app.py: Punto de entrada del dashboard
#     - --server.fileWatcherType=none: Desactiva el watcher (innecesario en producción)
CMD ["streamlit", "run", "dash/app.py", \
     "--server.fileWatcherType=none", \
     "--theme.primaryColor=#FF4B4B"]
