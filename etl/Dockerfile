# Usar una imagen base de Python oficial
FROM python:3.11-slim

# Establecer el directorio de trabajo en /app
WORKDIR /app

# Copiar el archivo de requerimientos
COPY requirements.txt .

# Instalar las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Copiar todo el código del dashboard al contenedor
COPY . .

# Exponer el puerto de la API
EXPOSE 8001

# Comando para arrancar la aplicación
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8001"]