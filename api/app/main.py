from flask import Flask, request, jsonify
import json
from pathlib import Path

app = Flask(__name__)

# Esta data se debe consumir desde data/json/api-data.json
try:
    data_file = Path(__file__).resolve().parents[2] / "data" / "json" / "api-data.json"
    with data_file.open("r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"mensaje": "Estos son los datos de la API", "status": "ok"}

@app.route("/")
def home():
    return "hola Docker y WSL2 tu api esta funcionando"

@app.route("/data",methods=["GET"])
def get_data():
    return data

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000,debug=True)