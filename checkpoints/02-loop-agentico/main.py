"""Checkpoint 02 — El loop agéntico completo (CLI interactiva).

Cerramos el círculo del checkpoint 01: cuando Claude pide una herramienta,
la ejecutamos, le devolvemos el resultado y lo dejamos continuar. Ese ciclo
—modelo decide, código ejecuta, modelo continúa— ES el agente.
"""

import json
import os
import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit(
        "Falta ANTHROPIC_API_KEY.\n"
        "Copia .env.example a .env en la carpeta principal del repo y agrega tu API key."
    )

client = anthropic.Anthropic()
MODEL = os.getenv("MODEL", "claude-sonnet-4-6")

# Límite de seguridad: si el modelo entrara en un ciclo de herramientas sin
# fin, cortamos. Todo loop agéntico en producción tiene uno.
MAX_ITERACIONES = 10

INVENTARIO = {
    "HW-LENOVO-T14": {"nombre": "Laptop Lenovo ThinkPad T14", "stock": 22, "precio_clp": 1150000},
    "HW-MBP-14": {"nombre": "MacBook Pro 14\"", "stock": 8, "precio_clp": 2650000},
    "LIC-M365-E3": {"nombre": "Licencia Microsoft 365 E3", "stock": 120, "precio_clp": 396000},
    "SRV-CELL-FS": {"nombre": "Hora célula full-stack", "stock": 640, "precio_clp": 48000},
}

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


def consultar_inventario(producto: str) -> str:
    consulta = producto.lower()
    resultados = {
        sku: datos
        for sku, datos in INVENTARIO.items()
        if consulta in datos["nombre"].lower() or consulta in sku.lower()
    }
    if not resultados:
        return f"Sin resultados para '{producto}'."
    return json.dumps(resultados, ensure_ascii=False)


def ejecutar_agente(conversacion: list[dict]) -> str:
    """El loop agéntico: repite hasta que Claude deje de pedir herramientas."""
    for _ in range(MAX_ITERACIONES):
        response = client.messages.create(
            model=MODEL,
            max_tokens=1500,
            tools=TOOLS,
            messages=conversacion,
        )

        # Caso 1: Claude terminó → devolvemos el texto y salimos.
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        # Caso 2: Claude pidió herramientas. Guardamos SU turno tal cual
        # (los bloques tool_use llevan un id que debemos referenciar)...
        conversacion.append({"role": "assistant", "content": response.content})

        # ...ejecutamos cada solicitud y devolvemos TODOS los resultados en
        # un único mensaje de usuario, emparejados por tool_use_id.
        resultados = []
        for bloque in response.content:
            if bloque.type == "tool_use":
                print(f"  [tool] {bloque.name}({json.dumps(bloque.input, ensure_ascii=False)})")
                salida = consultar_inventario(**bloque.input)
                resultados.append(
                    {"type": "tool_result", "tool_use_id": bloque.id, "content": salida}
                )
        conversacion.append({"role": "user", "content": resultados})

    return "(se alcanzó el límite de iteraciones)"


def main() -> None:
    print("Agente de inventario — escribe 'salir' para terminar.\n")
    conversacion: list[dict] = []
    while True:
        try:
            pregunta = input("Tú: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not pregunta or pregunta.lower() in {"salir", "exit", "quit"}:
            break
        conversacion.append({"role": "user", "content": pregunta})
        respuesta = ejecutar_agente(conversacion)
        # Guardamos la respuesta para que el agente tenga memoria de la charla.
        conversacion.append({"role": "assistant", "content": respuesta})
        print(f"\nAgente: {respuesta}\n")


if __name__ == "__main__":
    main()
