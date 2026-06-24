# =============================================================================
# Dockerfile para PostgreSQL - Base de datos de Movilidad RM
# =============================================================================
# Imagen base: PostgreSQL 15 sobre Alpine Linux (ligera, ~80 MB)
# Propósito: Levantar una instancia PostgreSQL con esquema y datos iniciales
# =============================================================================

# 1. Imagen base con versión fija para garantizar reproducibilidad
FROM postgres:15-alpine

# 2. Metadatos del contenedor (OCI estándar)
LABEL maintainer="equipo_dev@empresa.com"
LABEL org.opencontainers.image.title="PostgreSQL Movilidad RM"
LABEL org.opencontainers.image.version="1.0.0"
LABEL org.opencontainers.image.description="Base de datos PostgreSQL para el sistema de movilidad de la Región Metropolitana"

# 3. Variables de entorno con valores por defecto
#    Pueden sobreescribirse desde docker-compose o al ejecutar el contenedor
ENV POSTGRES_USER=estudiante \
    POSTGRES_PASSWORD=estudiante_password \
    POSTGRES_DB=movilidad_rm_db

# 4. Copiar scripts de inicialización al directorio estándar de PostgreSQL
#    - Los scripts en /docker-entrypoint-initdb.d/ se ejecutan SOLO en la primera
#      inicialización del volumen de datos, respetando orden alfabético.
#    - Se asigna el usuario postgres como propietario por seguridad.
COPY --chown=postgres:postgres 01-schema.sql /docker-entrypoint-initdb.d/
COPY --chown=postgres:postgres 02-data-db.sql /docker-entrypoint-initdb.d/

# 5. Exponer el puerto estándar de PostgreSQL
#    Esto documenta el puerto; el mapeo real se define en docker-compose.yml
EXPOSE 5432

# 6. Healthcheck para monitoreo del estado del contenedor
#    Verifica que PostgreSQL acepte conexiones cada 10 segundos
HEALTHCHECK --interval=10s --timeout=5s --start-period=30s --retries=3 \
    CMD pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB} || exit 1

# 7. El ENTRYPOINT y CMD se heredan de la imagen base (postgres:15-alpine)
#    No es necesario redefinirlos salvo personalización avanzada.
