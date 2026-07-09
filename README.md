# Proyecto Movilidad RM - Sistema de Analisis de Transporte

Sistema de analisis de movilidad urbana para la Region Metropolitana de Santiago, Chile. Integra una base de datos PostgreSQL, una API REST con FastAPI, un pipeline ETL y un dashboard interactivo con Streamlit, todo orquestado con Docker Compose.

---

## Arquitectura del Proyecto

```
proyecto_EP3/
├── api/                    # API REST (FastAPI + Gunicorn + Uvicorn)
│   ├── app/
│   │   ├── __init__.py
│   │   └── main.py         # Endpoints y logica de negocio
│   ├── .dockerignore
│   └── requirements.txt
├── dashboards/             # Dashboard interactivo (Streamlit)
│   ├── dash/
│   │   ├── __init__.py
│   │   └── app.py          # Visualizaciones por audiencia
│   ├── .streamlit/
│   │   └── config.toml     # Configuracion de Streamlit
│   ├── .dockerignore
│   └── requirements.txt
├── data/
│   ├── db/                 # Scripts SQL de inicializacion
│   │   ├── 01-schema.sql
│   │   └── 02-data-db.sql
│   ├── json/               # Datos JSON para la API
│   │   └── api-data.json
│   ├── processed/          # Datos procesados por el ETL
│   │   └── dataset_movilidad_rm.csv
│   └── raw/                # Datos crudos (CSVs fuente)
├── docker/                 # Dockerfiles de cada servicio
│   ├── api.dockerfile
│   ├── dashboard.dockerfile
│   └── db.dockerfile
├── etl/                    # Pipeline ETL
│   ├── pipeline_etl.py
│   └── notebooks/
├── tests/                  # Tests del proyecto
├── docker-compose.yml      # Orquestacion de servicios
├── .env                    # Variables de entorno (no commitear con secretos)
└── README.md
```

---

## Servicios

| Servicio | Tecnologia | Puerto | Descripcion |
|----------|-----------|--------|-------------|
| **psql-db** | PostgreSQL 15 Alpine | 5432 | Base de datos relacional con esquema de movilidad |
| **api** | FastAPI + Gunicorn/Uvicorn | 5000 | API REST con endpoints de consulta |
| **dashboard** | Streamlit | 8501 | Dashboard interactivo con 3 vistas (Ejecutivo, Tecnico, Operativo) |

---

## Requisitos Previos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (v20.10+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+ incluido en Docker Desktop)
- Puerto 5432, 5000 y 8501 disponibles en el host

Para verificar la instalacion:

```bash
docker --version
docker compose version
```

---

## Ejecucion del Proyecto

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd proyecto_EP3
```

### 2. Construir y levantar todos los servicios

```bash
docker compose up -d --build
```

Este comando:
- Construye las 3 imagenes Docker (db, api, dashboard)
- Crea la red interna `app-network`
- Crea el volumen persistente `psql_data`
- Levanta los contenedores en el orden correcto:
  1. `psql-db` (base de datos)
  2. `api` (espera a que la DB pase healthcheck)
  3. `dashboard` (espera a que la API pase healthcheck)

### 3. Verificar que los servicios estan saludables

```bash
docker compose ps
```

Todos los servicios deben mostrar estado `healthy`:

```
NAME                              STATUS          PORTS
cont-db-psql-data-service         Up (healthy)    0.0.0.0:5432->5432/tcp
cont-api-flask-service            Up (healthy)    0.0.0.0:5000->5000/tcp
cont-dashboard-streamlit-service  Up (healthy)    0.0.0.0:8501->8501/tcp
```

### 4. Acceder a los servicios

| Servicio | URL |
|----------|-----|
| API REST (documentacion interactiva) | http://localhost:5000/docs |
| API REST (raiz) | http://localhost:5000/ |
| Dashboard Streamlit | http://localhost:8501 |

---

## Endpoints de la API

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Health check - verifica que la API funciona |
| GET | `/api/comunas` | Lista todas las comunas con ingreso promedio |
| GET | `/api/paraderos` | Lista todos los paraderos con coordenadas |
| GET | `/api/recorridos` | Lista recorridos con empresa y capacidad |
| GET | `/api/monitoreo` | Datos de monitoreo de viajes |
| GET | `/api/analiticas` | Dataset consolidado (joins de todas las tablas) |
| GET | `/docs` | Documentacion interactiva Swagger UI |

---

## Pipeline ETL

El pipeline ETL extrae datos desde la API y genera archivos CSV procesados.

### Ejecutar el ETL (con los contenedores levantados)

```bash
cd etl
pip install pandas requests
python pipeline_etl.py
```

Genera los siguientes archivos CSV:
- `comunas.csv`
- `paraderos.csv`
- `recorridos.csv`
- `monitoreo_viajes.csv`
- `dataset_movilidad_rm.csv` (consolidado)

---

## Comandos Utiles

### Ver logs de un servicio especifico

```bash
docker compose logs -f api
docker compose logs -f psql-db
docker compose logs -f dashboard
```

### Detener todos los servicios

```bash
docker compose down
```

### Detener y eliminar volumenes (borra datos de la DB)

```bash
docker compose down -v
```

### Reconstruir un servicio especifico

```bash
docker compose up -d --build api
docker compose up -d --build dashboard
```

### Acceder a la base de datos por terminal

```bash
docker exec -it cont-db-psql-data-service psql -U estudiante -d movilidad_rm_db
```

### Desarrollo con hot-reload (watch mode)

```bash
docker compose watch
```

Sincroniza cambios locales en `api/` y `dashboards/` automaticamente con los contenedores.

---

## Variables de Entorno

Las credenciales de la base de datos se configuran en `docker-compose.yml`:

| Variable | Valor por defecto | Descripcion |
|----------|-------------------|-------------|
| `POSTGRES_USER` | estudiante | Usuario de PostgreSQL |
| `POSTGRES_PASSWORD` | estudiante_password | Contrasena de PostgreSQL |
| `POSTGRES_DB` | movilidad_rm_db | Nombre de la base de datos |
| `DATABASE_HOST` | psql-db | Host de la DB (nombre del servicio Docker) |
| `DATABASE_PORT` | 5432 | Puerto de PostgreSQL |

---

## Solucion de Problemas

### La API no conecta a la base de datos

```bash
# Verificar que la DB esta healthy
docker compose ps psql-db

# Ver logs de la DB
docker compose logs psql-db

# Reiniciar solo la API
docker compose restart api
```

### El dashboard no carga datos

Verificar que el archivo `data/processed/dataset_movilidad_rm.csv` existe y tiene contenido. Este archivo se genera ejecutando el pipeline ETL.

### Puertos en uso

Si algun puerto esta ocupado, modificar el mapeo en `docker-compose.yml`:

```yaml
ports:
  - "NUEVO_PUERTO:5432"  # Para la DB
  - "NUEVO_PUERTO:5000"  # Para la API
  - "NUEVO_PUERTO:8501"  # Para el Dashboard
```

### Reiniciar todo desde cero

```bash
docker compose down -v --rmi local
docker compose up -d --build
```

---

## Tecnologias

- **Python 3.11** - Lenguaje principal
- **FastAPI** - Framework web asincrono para la API
- **Gunicorn + Uvicorn** - Servidor ASGI de produccion
- **PostgreSQL 15** - Base de datos relacional
- **Streamlit** - Framework para dashboards interactivos
- **Plotly** - Visualizaciones interactivas
- **Pandas** - Manipulacion de datos
- **Docker & Docker Compose** - Contenedorizacion y orquestacion
