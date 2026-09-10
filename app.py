from flask import Flask, request, jsonify
from datetime import datetime

from model.predictor import predecir_severidad

app = Flask(__name__)

CAMPOS_REQUERIDOS = ["date", "latitude", "longitude", "depth_km"]


def validar_input(data):
    """
    Valida los datos recibidos para una predicción (vengan por query string
    en un GET, o por JSON en un POST). Devuelve (datos_limpios, None) si todo
    es correcto, o (None, "mensaje de error") si algo falla.
    """
    if data is None:
        return None, "No se han recibido datos en la petición."

    faltantes = [campo for campo in CAMPOS_REQUERIDOS if campo not in data]
    if faltantes:
        return None, f"Faltan los siguientes campos: {', '.join(faltantes)}."

    #date: formato YYYY-MM-DD
    try:
        datetime.strptime(str(data["date"]), "%Y-%m-%d")
    except (ValueError, TypeError):
        return None, "El campo 'date' debe tener el formato YYYY-MM-DD, por ejemplo '2024-03-15'."

    #latitude: número entre -90 y 90
    try:
        latitude = float(data["latitude"])
    except (ValueError, TypeError):
        return None, "El campo 'latitude' debe ser un número."
    if not -90 <= latitude <= 90:
        return None, "El campo 'latitude' debe estar entre -90 y 90."

    #longitude: número entre -180 y 180
    try:
        longitude = float(data["longitude"])
    except (ValueError, TypeError):
        return None, "El campo 'longitude' debe ser un número."
    if not -180 <= longitude <= 180:
        return None, "El campo 'longitude' debe estar entre -180 y 180."

    # depth_km: número no negativo
    try:
        depth_km = float(data["depth_km"])
    except (ValueError, TypeError):
        return None, "El campo 'depth_km' debe ser un número."
    if depth_km < 0:
        return None, "El campo 'depth_km' no puede ser negativo."

    datos_limpios = {
        "date": data["date"],
        "latitude": latitude,
        "longitude": longitude,
        "depth_km": depth_km,
    }
    return datos_limpios, None


@app.route("/", methods=["GET"])
def home():
    """Landing page: explica cómo usar el resto de la API."""
    return jsonify({
        "mensaje": "API de predicción de severidad de terremotos.",
        "endpoints": {
            "/predict": {
                "metodo": "GET (también acepta POST con JSON)",
                "descripcion": "Predice si un terremoto será severo a partir de sus datos.",
                "ejemplo_get": "/predict?date=2024-03-15&latitude=36.874&longitude=69.947&depth_km=54.3",
                "ejemplo_post_json": {
                    "date": "2024-03-15",
                    "latitude": 36.874,
                    "longitude": 69.947,
                    "depth_km": 54.3
                },
                "respuesta_ejemplo": {
                    "es_severo": 0,
                    "probabilidad_severo": 0.319
                }
            }
        }
    })


@app.route("/predict", methods=["GET", "POST"])
def predict():
    #GET: los datos vienen como parámetros en la URL (?date=...&latitude=...)
    #POST: los datos vienen como JSON en el cuerpo de la petición
    if request.method == "GET":
        data = request.args
    else:
        data = request.get_json(silent=True)

    datos_limpios, error = validar_input(data)
    if error:
        return jsonify({"error": error}), 400

    try:
        resultado = predecir_severidad(**datos_limpios)
    except Exception as e:
        return jsonify({"error": f"No se ha podido generar la predicción: {e}"}), 500

    return jsonify(resultado), 200


#TERCER ENDPOINT — descomentar para el redespliegue en directo.
# Añade al resultado del modelo una clasificación de riesgo legible
# (bajo / medio / alto) en vez de solo la probabilidad en crudo.
# ------------------------------------------------------------------
 def clasificar_riesgo(probabilidad):
   if probabilidad < 0.33:
        return "bajo"
    elif probabilidad < 0.66:
        return "medio"
    else:
        return "alto"

@app.route("/predict/riesgo", methods=["GET", "POST"])
def predict_riesgo():
    if request.method == "GET":
        data = request.args
    else:
        data = request.get_json(silent=True)
    datos_limpios, error = validar_input(data)
   if error:
        return jsonify({"error": error}), 400

    try:
         resultado = predecir_severidad(**datos_limpios)
     except Exception as e:
         return jsonify({"error": f"No se ha podido generar la predicción: {e}"}), 500

     resultado["nivel_riesgo"] = clasificar_riesgo(resultado["probabilidad_severo"])
return jsonify(resultado), 200


if __name__ == "__main__":
    app.run(debug=True)

