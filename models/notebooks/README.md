# 🚍 Proyecto Movilidad RM - Pipeline End-to-End con Machine Learning

## 📌 Descripción

Este proyecto implementa una solución End-to-End para el análisis de datos de movilidad de la Región Metropolitana de Chile.

La solución integra un proceso completo de Ciencia de Datos que incluye:

- Extracción y procesamiento de datos.
- Entrenamiento de modelos de Machine Learning.
- Selección automática del mejor modelo.
- API REST desarrollada con FastAPI.
- Dashboard interactivo desarrollado con Streamlit.
- Base de datos PostgreSQL.
- Contenedorización mediante Docker Compose.

El sistema permite consultar información de movilidad y realizar predicciones del tiempo promedio de viaje utilizando un modelo entrenado con Scikit-Learn.

---

# 🏗 Arquitectura del Proyecto

```
                ┌──────────────────────┐
                │   Dashboard          │
                │     Streamlit        │
                └──────────┬───────────┘
                           │
                     HTTP Requests
                           │
                ┌──────────▼───────────┐
                │      FastAPI         │
                │      REST API        │
                └───────┬───────┬──────┘
                        │       │
                        │       │
                        │       ▼
                        │  Modelo ML
                        │ best_model.pkl
                        │
                        ▼
                  PostgreSQL
```

---

# 📂 Estructura del Proyecto

```
EP2-pipeline-end-to-end-dashboard/

│
├── api/
│   ├── app/
│   │   ├── main.py
│   │   └── ml_service.py
│   └── requirements.txt
│
├── dashboards/
│   ├── dash/
│   ├── dato_crudo/
│   └── requirements.txt
│
├── data/
│   ├── db/
│   ├── json/
│   ├── processed/
│   └── raw/
│
├── docker/
│   ├── api.dockerfile
│   ├── dashboard.dockerfile
│   └── db.dockerfile
│
├── etl/
│
├── models/
│   └── artifacts/
│       ├── best_model.pkl
│       └── metrics.json
│
├── notebooks/
│
├── docker-compose.yml
└── README.md
```

---

# 🧰 Tecnologías utilizadas

- Python 3.11
- FastAPI
- Streamlit
- PostgreSQL
- Docker
- Docker Compose
- Pandas
- NumPy
- Scikit-Learn
- Joblib
- Gunicorn
- Uvicorn

---

# 🤖 Modelo de Machine Learning

Se entrenaron distintos modelos de regresión para estimar el tiempo promedio de viaje.

Los modelos fueron evaluados utilizando:

- MAE
- RMSE
- R²

El mejor modelo fue almacenado automáticamente utilizando Joblib.

```
models/artifacts/best_model.pkl
```

Las métricas obtenidas se almacenan en:

```
models/artifacts/metrics.json
```

---

# 🚀 Ejecución del proyecto

## Clonar repositorio

```bash
git clone <URL_DEL_REPOSITORIO>

cd EP2-pipeline-end-to-end-dashboard
```

---

## Construir los contenedores

```bash
docker compose build
```

---

## Levantar los servicios

```bash
docker compose up
```

---

## Servicios disponibles

| Servicio | URL |
|----------|----------------------|
| API | http://localhost:5000 |
| Swagger | http://localhost:5000/docs |
| Dashboard | http://localhost:8501 |
| PostgreSQL | localhost:5432 |

---

# 📡 Endpoints principales

| Método | Endpoint | Descripción |
|---------|----------|-------------|
| GET | /api/comunas | Lista de comunas |
| GET | /api/paraderos | Lista de paraderos |
| GET | /api/recorridos | Lista de recorridos |
| GET | /api/monitoreo | Información de monitoreo |
| GET | /api/analiticas | Analíticas del sistema |
| POST | /api/predict | Predicción mediante Machine Learning |

---

# 📊 Ejemplo de predicción

Solicitud:

```json
{
  "comuna_id": 2,
  "comuna": "Maipu",
  "ingreso_promedio_hogar": 950000,
  "paradero_id": 2,
  "latitud": -33.51,
  "longitud": -70.76,
  "recorrido_id": 2,
  "recorrido": "405",
  "empresa_operadora": "STP",
  "capacidad_pasajeros": 100,
  "flujo_pasajeros": 1800,
  "velocidad_promedio": 25.5,
  "hora": 8,
  "dia": 15,
  "mes": 3
}
```

Respuesta:

```json
{
  "status": "success",
  "prediccion": 34.86,
  "unidad": "minutos"
}
```

---

# 📈 Dashboard

El dashboard desarrollado con Streamlit permite visualizar información relevante sobre la movilidad de la Región Metropolitana mediante gráficos interactivos y consultas a la API.

---

# 🐳 Docker

La solución se encuentra completamente contenerizada mediante Docker Compose.

Los servicios incluidos son:

- PostgreSQL
- FastAPI
- Streamlit

---

# 👥 Autores

Proyecto desarrollado para la asignatura **Programación para Ciencia de Datos**.

## Capturas

### Swagger

![Swagger](docs/swagger.png)

### Dashboard

![Dashboard](docs/dashboard.png)

### Predicción

![Predicción](docs/predict.png)