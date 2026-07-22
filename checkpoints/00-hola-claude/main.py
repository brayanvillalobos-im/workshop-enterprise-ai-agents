"""Checkpoint 00 — Hola Claude: la primera llamada al SDK.

Sin herramientas, sin loop: una request, una respuesta. Sirve para verificar
que el entorno (Python + API key) quedó bien configurado.
"""

import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# La consola de Windows usa cp1252 por defecto y truena si Claude responde
# con un emoji. Forzamos UTF-8 (y reemplazo como red de seguridad).
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# El .env vive en la raíz del repo (dos carpetas arriba); así la key se
# configura UNA vez y todos los checkpoints la comparten.
load_dotenv(Path(__file__).resolve().parents[2] / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit(
        "Falta ANTHROPIC_API_KEY.\n"
        "Copia .env.example a .env en la carpeta principal del repo y agrega tu API key."
    )

client = anthropic.Anthropic()  # lee ANTHROPIC_API_KEY del entorno

response = client.messages.create(
    model=os.getenv("MODEL", "claude-sonnet-4-6"),
    max_tokens=500,
    messages=[
        {
            "role": "user",
            "content": "Preséntate en dos frases y dime qué es un agente de IA.",
        }
    ],
)

# La respuesta es una lista de bloques; filtramos los de texto porque otros
# tipos (thinking, tool_use) pueden aparecer según la configuración.
for bloque in response.content:
    if bloque.type == "text":
        print(bloque.text)

print(f"\n--- stop_reason: {response.stop_reason} | tokens: {response.usage.output_tokens} ---")
