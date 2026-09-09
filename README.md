# Despliegue Terremotos — API de predicción de severidad sísmica

Despliegue de un modelo de Machine Learning como API REST, accesible públicamente a través de Render.

## Qué hace

A partir de los datos de un terremoto (fecha, latitud, longitud y profundidad), el modelo predice si será severo y con qué probabilidad, usando un árbol de decisión entrenado con datos históricos de sismicidad.

## URL pública

**https://despliegue-terremotos.onrender.com**

> Nota: al estar en el plan gratuito de Render, el servicio puede tardar 30-60 segundos en responder si lleva más de 15 minutos sin recibir tráfico.

## Endpoints

### `GET /`
Landing page. Devuelve información sobre cómo usar el resto de la API.

### `GET /predict` o `POST /predict`
Predice si un terremoto será severo.

**Parámetros** (como query string en GET, o como JSON en POST):

| Campo | Tipo | Descripción |
|---|---|---|
| `date` | string | Fecha en formato `YYYY-MM-DD` |
| `latitude` | float | Latitud, entre -90 y 90 |
| `longitude` | float | Longitud, entre -180 y 180 |
| `depth_km` | float | Profundidad del terremoto en km (≥ 0) |

**Ejemplo (GET):**
```
GET /predict?date=2024-03-15&latitude=36.874&longitude=69.947&depth_km=54.3
```

**Respuesta:**
```json
{
  "es_severo": 0,
  "probabilidad_severo": 0.319
}
```

Si falta algún campo o el formato es incorrecto, la API responde con código `400` y un mensaje de error claro en vez de un error 500.

### `GET /predict/riesgo` o `POST /predict/riesgo`
Igual que `/predict`, pero además clasifica la probabilidad en un nivel de riesgo legible.

**Respuesta:**
```json
{
  "es_severo": 0,
  "probabilidad_severo": 0.319,
  "nivel_riesgo": "bajo"
}
```
(`"bajo"` si probabilidad < 0.33, `"medio"` si < 0.66, `"alto"` en el resto de casos)

## Cómo probarlo con Python

```python
import requests

url = "https://despliegue-terremotos.onrender.com/predict"
resp = requests.get(url, params={
    "date": "2024-03-15",
    "latitude": 36.874,
    "longitude": 69.947,
    "depth_km": 54.3
})
print(resp.status_code, resp.json())
```

## Ejecutar en local

```bash
pip install -r requirements.txt
python app.py
```
La app arranca en `http://127.0.0.1:5000`.

## Estructura del proyecto

```
.
├── app.py                  # API Flask: landing page, /predict, /predict/riesgo
├── requirements.txt
└── model/
    ├── predictor.py         # función predecir_severidad()
    ├── decision_tree_sismicidad.joblib
    ├── scaler.joblib
    └── ordinal_enc.joblib
```

## Despliegue

Desplegado en [Render](https://render.com) como Web Service, conectado a la rama `main` de este repositorio.
- **Start command:** `gunicorn app:app`
- **Build:** automático a partir de `requirements.txt`

## Flujo de trabajo (Git Flow)

- `main`: código en producción, solo recibe merges vía Pull Request.
- `develop`: integración de funcionalidades antes de pasar a producción.
- `feature/*`: una funcionalidad nueva por rama, con PR hacia `develop` (o `main` para el redespliegue en directo).
  
- `develop`: integración de funcionalidades antes de pasar a producción.
- `feature/*`: una funcionalidad nueva por rama, con PR hacia `develop` (o `main` para el redespliegue en directo).
