# docker/etl.dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias directamente (o usar un requirements.txt si lo creas en etl/)
RUN pip install --no-cache-dir pandas requests

# Copiar el script
COPY ./etl/pipeline_etl.py /app/pipeline_etl.py

# Ejecutar el script por defecto
CMD ["python", "pipeline_etl.py"]