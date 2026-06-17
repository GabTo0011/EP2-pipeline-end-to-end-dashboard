# 1. Usa una versión específica y estable en lugar de 'latest' para evitar fallos si MySQL se actualiza
FROM mysql:8.4.0

# 2. Buenas prácticas: Añadir metadatos para auditoría y mantenimiento del equipo de desarrollo
LABEL maintainer="tu_equipo_dev@empresa.com"
LABEL version="1.0.0"
LABEL description="Imagen corporativa optimizada para MySQL con configuraciones de seguridad"

# 3. Establece el directorio de trabajo oficial para scripts de inicialización automatizada
WORKDIR /docker-entrypoint-initdb.d

# 4. Copia archivos de configuración personalizados con permisos restringidos de lectura
COPY --chown=mysql:mysql ./config/custom.cnf /etc/mysql/conf.d/

# 5. Copia todos los script de inicialización (ej. crear tablas, poblar) que se ejecutará SOLO la primera vez, repetando el orden alfabético.
COPY --chown=mysql:mysql ./*.sql .

# 6. Informa el puerto por el que escuchará el contenedor dentro de su red privada
EXPOSE 3306
