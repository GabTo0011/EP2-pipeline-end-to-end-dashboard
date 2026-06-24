# =============================================================================
# Dockerfile para la API REST - Proyecto Movilidad RM
# =============================================================================
# Imagen base: Python 3.11 slim (Debian, ~150 MB)
# Propósito: Servir la API FastAPI con Gunicorn + Uvicorn workers en producción
# =============================================================================

# 1. Imagen base con versión fija para reproducibilidad
#    Se usa "slim" para reducir superficie de ataque y tamaño de imagen
FROM python:3.11-slim

# 2. Metadatos del contenedor (OCI estándar)
LABEL maintainer="equipo_dev@empresa.com"
LABEL org.opencontainers.image.title="API Movilidad RM"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="API REST FastAPI para el sistema de movilidad de la Región Metropolitana"

# 3. Variables de entorno para Python
#    - PYTHONDONTWRITEBYTECODE: Evita generar archivos .pyc innecesarios
#    - PYTHONUNBUFFERED: Logs en tiempo real sin buffer (importante para Docker)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 4. Establecer directorio de trabajo dentro del contenedor
WORKDIR /app

# 5. Instalar dependencias del sistema necesarias (si las hubiera) y limpiar cache
#    Se ejecuta en una sola capa para reducir tamaño de imagen
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# 6. Copiar SOLO el archivo de dependencias primero
#    Esto aprovecha la caché de capas de Docker: si requirements.txt no cambia,
#    no se reinstalan las dependencias al reconstruir la imagen
COPY requirements.txt .

# 7. Instalar dependencias de Python
#    --no-cache-dir: No almacena cache de pip (reduce tamaño de imagen)
#    --upgrade pip: Asegura tener la última versión del instalador
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 8. Copiar el código fuente de la aplicación
#    El .dockerignore excluye archivos innecesarios (venv, __pycache__, etc.)
COPY . .

# 9. Crear usuario no-root para ejecutar la aplicación (seguridad)
#    Nunca ejecutar servicios como root en producción
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app

USER appuser

# 10. Exponer el puerto de la API
#     Documenta el puerto; el mapeo real se define en docker-compose.yml
EXPOSE 5000

# 11. Healthcheck para monitoreo del estado del servicio
#     Verifica que la API responda correctamente cada 30 segundos
HEALTHCHECK --interval=30s --timeout=10s --start-period=15s --retries=3 \
    CMD curl --fail http://localhost:5000/ || exit 1

# 12. Comando de inicio: Gunicorn con Uvicorn workers (ASGI para FastAPI)
#     - worker-class: uvicorn.workers.UvicornWorker para soporte async
#     - workers: 4 procesos para manejar concurrencia
#     - bind: Escucha en todas las interfaces en el puerto 5000
#     - access-logfile: Logs de acceso a stdout para Docker
CMD ["gunicorn", \
     "--bind", "0.0.0.0:5000", \
     "--workers", "4", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--access-logfile", "-", \
     "--error-logfile", "-", \
     "app.main:app"]
