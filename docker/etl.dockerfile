# docker/etl.dockerfile
FROM python:3.11-slim

WORKDIR /app

# 6. Copiar SOLO el archivo de dependencias primero
#    Esto aprovecha la caché de capas de Docker: si requirements.txt no cambia,
#    no se reinstalan las dependencias al reconstruir la imagen
COPY requirements.txt .

# 7. Instalar dependencias de Python
#    --no-cache-dir: No almacena cache de pip (reduce tamaño de imagen)
#    --upgrade pip: Asegura tener la última versión del instalador
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copiar el script
COPY ./app/pipeline_etl.py /app/pipeline_etl.py

# Ejecutar el script por defecto
CMD ["python", "pipeline_etl.py"]