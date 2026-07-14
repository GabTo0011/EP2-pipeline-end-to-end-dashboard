import os
import sys

# 1. ESTO TIENE QUE IR PRIMERO QUE TODO: Modificar las rutas de Python
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# 2. Importaciones de dependencias y módulos del proyecto
import pytest
from fastapi.testclient import TestClient
from api.main import app   

# Creamos el cliente de pruebas de FastAPI
client = TestClient(app)

def test_read_home():
    """Valida que el endpoint raíz responda correctamente (200 OK)"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "Operativa"

def test_predict_endpoint_success():
    """Valida que el endpoint de predicción reciba y procese un JSON válido"""
    payload = {
        "Comuna": "Santiago",
        "Tipo_dia": "Laboral",
        "Media_hora": "08:00:00"
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert "subidas_promedio_estimadas" in data
    assert "cluster_comportamiento" in data
    assert data["comuna"] == "SANTIAGO"

def test_predict_endpoint_validation_error():
    """Valida que la API falle con código 400 si se envían campos vacíos"""
    payload = {
        "Comuna": "",
        "Tipo_dia": "Laboral",
        "Media_hora": ""
    }
    response = client.post("/api/v1/predict", json=payload)
    assert response.status_code == 400