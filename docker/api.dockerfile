# 1. Imagen base oficial de Python (versión ligera)
FROM python:3.11-slim

# 2. Establecer el directorio de trabajo dentro del contenedor
WORKDIR /app

# 3. Copiar primero el archivo de dependencias para aprovechar la caché de Docker
COPY requirements.txt .

# 4. Instalar las dependencias de Python sin guardar archivos temporales
RUN pip install --no-cache-dir -r requirements.txt
# RUN pip install --no-cache-dir -r flask

# 5. Copiar el resto del código fuente del proyecto
COPY . .

# 6. Exponer el puerto predeterminado en el que corre Flask
EXPOSE 5000

# 7. Definir las variables de entorno necesarias para Flask
ENV FLASK_APP=app/main.py
ENV FLASK_RUN_HOST=0.0.0.0

# 8. Comando para arrancar la aplicación en modo producción usando Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.main:app"]
