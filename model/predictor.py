import joblib
import pandas as pd
import numpy as np

# Cargar una sola vez al importar el módulo
modelo = joblib.load("model/decision_tree_sismicidad.joblib")
scaler = joblib.load("model/scaler.joblib")
ordinal_enc = joblib.load("model/ordinal_enc.joblib")


def predecir_severidad(date, latitude, longitude, depth_km):
    """
    Recibe los datos crudos de un terremoto y devuelve si es severo.

    Parámetros:
        date (str): fecha en formato 'YYYY-MM-DD'
        latitude (float), longitude (float), depth_km (float)

    Devuelve:
        dict con 'es_severo' (0/1) y 'probabilidad_severo' (float)
    """
    X = pd.DataFrame([{
        "date": date, "latitude": latitude,
        "longitude": longitude, "depth_km": depth_km
    }])

    X["date"] = pd.to_datetime(X["date"])
    X["mes"] = X["date"].dt.month
    X["año"] = X["date"].dt.year

    X["cinturon_fuego"] = (
        (
            ((X["longitude"] >= 100) & (X["longitude"] <= 180)) |
            ((X["longitude"] >= -180) & (X["longitude"] <= -60))
        ) &
        (X["latitude"] >= -60) & (X["latitude"] <= 70)
    ).astype(int)

    X["prof_grupo"] = pd.cut(
        X["depth_km"],
        bins=[-np.inf, 70, 300, np.inf],
        labels=["superficial", "intermedio", "profundo"]
    )
    X["prof_grupo"] = ordinal_enc.transform(X[["prof_grupo"]])

    cols_escalar = ["latitude", "longitude", "depth_km", "mes", "año"]
    X[cols_escalar] = scaler.transform(X[cols_escalar])

    X_final = X[["latitude", "longitude", "depth_km", "mes", "año", "cinturon_fuego", "prof_grupo"]]

    prediccion = int(modelo.predict(X_final)[0])
    probabilidad = float(modelo.predict_proba(X_final)[0][1])

    return {"es_severo": prediccion, "probabilidad_severo": round(probabilidad, 4)}