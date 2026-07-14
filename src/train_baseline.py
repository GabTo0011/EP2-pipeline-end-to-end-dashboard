import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
import pickle
import os

print("[INFO] Generando datos sintéticos para Red Movilidad...")
np.random.seed(42)
N_SAMPLES = 1000
data = {
    'feature_1': np.random.rand(N_SAMPLES),
    'feature_2': np.random.rand(N_SAMPLES) * 100,
    'feature_3': np.random.choice([0, 1], N_SAMPLES),
    'target_subidas': np.random.randint(5, 150, N_SAMPLES) # Subidas promedio
}
df = pd.DataFrame(data)

X = df.drop('target_subidas', axis=1)
y = df['target_subidas']

# 1. ENTRENAR MODELO SUPERVISADO (REGRESIÓN)
print("[INFO] Entrenando modelo de regresión...")
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
reg_model = LinearRegression()
reg_model.fit(X_train, y_train)

# 2. ENTRENAR MODELO NO SUPERVISADO (KMEANS)
print("[INFO] Entrenando modelo de clustering (KMeans)...")
kmeans_model = KMeans(n_clusters=4, random_state=42, n_init=10)
kmeans_model.fit(X)

# 3. EXPORTAR AMBOS ARTEFACTOS CON LOS NOMBRES CORRECTOS
os.makedirs('models', exist_ok=True)

ruta_sup = "models/modelo_regresion.pkl"
ruta_no_sup = "models/modelo_kmeans.pkl"

with open(ruta_sup, "wb") as f:
    pickle.dump(reg_model, f)
with open(ruta_no_sup, "wb") as f:
    pickle.dump(kmeans_model, f)

print(f"[SUCCESS] Guardado: {ruta_sup}")
print(f"[SUCCESS] Guardado: {ruta_no_sup}")