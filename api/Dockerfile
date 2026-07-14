# Usar una imagen base de Python oficial
FROM python:3.11-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo de requerimientos primero para aprovechar el cache de Docker
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY ./app ./app

# Comando para ejecutar la API cuando el contenedor inicie
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]