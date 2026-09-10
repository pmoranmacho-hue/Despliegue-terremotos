import requests

BASE_URL = "https://despliegue-terremotos.onrender.com"

# 1. Probar la landing page
print("=== Landing page ===")
response = requests.get(f"{BASE_URL}/")
print(response.json())

# 2. Probar /predict con datos válidos
print("\n=== /predict con datos válidos ===")
datos = {
    "date": "2024-03-15",
    "latitude": 36.874,
    "longitude": 69.947,
    "depth_km": 54.3
}
response = requests.get(f"{BASE_URL}/predict", params=datos)
print(response.json())

# 3. Probar el manejo de errores (latitud fuera de rango)
print("\n=== /predict con error (latitud inválida) ===")
datos_error = {
    "date": "2024-03-15",
    "latitude": 200,  # fuera de rango
    "longitude": 69.947,
    "depth_km": 54.3
}
response = requests.get(f"{BASE_URL}/predict", params=datos_error)
print(f"Status code: {response.status_code}")
print(response.json())

# 4. Probar /predict/riesgo (nuevo endpoint activado)
print("\n=== /predict/riesgo ===")
response = requests.get(f"{BASE_URL}/predict/riesgo", params=datos)
print(response.json())
