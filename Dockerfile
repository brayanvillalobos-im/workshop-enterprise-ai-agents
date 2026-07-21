# Imagen slim: suficiente para FastAPI + SDK de Anthropic, y pesa ~10x menos
# que la imagen completa de Python.
FROM python:3.12-slim

WORKDIR /app

# Copiamos requirements.txt ANTES que el código: Docker cachea cada capa, así
# que si solo cambia el código (lo habitual), no se reinstalan dependencias.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

# Cloud Run (y otros serverless de contenedores) inyectan el puerto en $PORT.
# Definimos 8080 como default para poder correr la imagen también en local.
ENV PORT=8080

# Forma "shell" del CMD para que $PORT se expanda en tiempo de ejecución.
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
