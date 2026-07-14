from pathlib import Path
import joblib

MODEL_PATH = Path("/app/models/artifacts/best_model.pkl")

if not MODEL_PATH.exists():
    raise FileNotFoundError(f"No existe el modelo: {MODEL_PATH}")

modelo = joblib.load(MODEL_PATH)


def predecir(df):
    return modelo.predict(df)