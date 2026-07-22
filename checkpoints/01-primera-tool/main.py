"""Checkpoint 01 — Primera herramienta (SIN loop, a propósito).

Aquí pasa algo clave: Claude NO ejecuta código. Cuando decide usar una
herramienta, PAUSA su respuesta (stop_reason == "tool_use") y nos pide que la
ejecutemos nosotros. Este script se detiene justo en esa pausa para que la
veas con tus propios ojos. Cerrar el círculo es tarea del checkpoint 02.
"""

import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

# La consola de Windows usa cp1252 por defecto y truena si Claude responde
# con un emoji. Forzamos UTF-8 (y reemplazo como red de seguridad).
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit(
        "Falta ANTHROPIC_API_KEY.\n"
        "Copia .env.example a .env en la carpeta principal del repo y agrega tu API key."
    )

client = anthropic.Anthropic()

# Mini-inventario inline: lo justo para demostrar el concepto.
INVENTARIO = {
    "HW-LENOVO-T14": {"nombre": "Laptop Lenovo ThinkPad T14", "stock": 22, "precio_clp": 1150000},
    "HW-MBP-14": {"nombre": "MacBook Pro 14\"", "stock": 8, "precio_clp": 2650000},
    "LIC-M365-E3": {"nombre": "Licencia Microsoft 365 E3", "stock": 120, "precio_clp": 396000},
}

# La DEFINICIÓN de la herramienta: nombre + descripción + schema de entrada.
# Esto es lo único que Claude ve; con esto decide cuándo y cómo llamarla.
TOOLS = [
    {
        "name": "consultar_inventario",
        "description": "Busca un producto en el inventario y devuelve stock y precio en CLP.",
        "input_schema": {
            "type": "object",
            "properties": {
                "producto": {"type": "string", "description": "Nombre o SKU del producto"},
            },
            "required": ["producto"],
        },
    }
]

response = client.messages.create(
    model=os.getenv("MODEL", "claude-sonnet-4-6"),
    max_tokens=1000,
    tools=TOOLS,
    messages=[{"role": "user", "content": "¿Cuántas laptops Lenovo tenemos en stock?"}],
)

print(f"stop_reason: {response.stop_reason}\n")

for bloque in response.content:
    if bloque.type == "text":
        print(f"[texto]    {bloque.text}")
    elif bloque.type == "tool_use":
        print(f"[tool_use] Claude pide ejecutar: {bloque.name}")
        print(f"           argumentos: {json.dumps(bloque.input, ensure_ascii=False)}")
        print(f"           id: {bloque.id}")

print(
    "\nObserva: la conversación quedó EN PAUSA. Claude está esperando que"
    "\nejecutemos la herramienta y le devolvamos el resultado (tool_result)."
    "\nEso —el loop— es exactamente lo que agrega el checkpoint 02."
)
