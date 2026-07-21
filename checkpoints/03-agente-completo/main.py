"""Checkpoint 03 — Agente completo: 3 herramientas + system prompt (CLI).

Mismo loop del checkpoint 02, ahora con el set completo de herramientas y un
system prompt que define rol y reglas. Este archivo duplica adrede las
implementaciones de app/tools.py: en el workshop la progresión pedagógica
importa más que el DRY. La versión "de producción" (modular y con API HTTP)
vive en app/ y es idéntica en su núcleo.
"""

import json
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import anthropic
from dotenv import load_dotenv

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "app" / "data"  # reutilizamos los datos de la app final

load_dotenv(REPO_ROOT / ".env")

if not os.getenv("ANTHROPIC_API_KEY"):
    sys.exit(
        "Falta ANTHROPIC_API_KEY.\n"
        "Copia .env.example a .env en la carpeta principal del repo y agrega tu API key."
    )

client = anthropic.Anthropic()
MODEL = os.getenv("MODEL", "claude-sonnet-4-6")
MAX_ITERACIONES = 10

# El system prompt convierte un "modelo con herramientas" en un AGENTE con
# rol, criterio y reglas de negocio.
SYSTEM_PROMPT = """\
Eres el "Asistente de Operaciones" de una consultora tecnológica chilena.
Ayudas al equipo interno a consultar inventario, preparar cotizaciones y
responder preguntas sobre políticas internas.

Reglas:
- Usa las herramientas en vez de inventar datos; si no hay resultados, dilo.
- Para cotizar, consulta primero el inventario y usa los precios reales.
- Los montos están en CLP; formatéalos con separador de miles.
- Responde en español, breve y profesional.
"""

TOOLS = [
    {
        "name": "consultar_inventario",
        "description": (
            "Busca productos o servicios en el inventario por nombre, SKU o "
            "categoría (licencias, hardware, servicios, capacitacion). "
            "Devuelve stock, precio en CLP y SKU."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "producto": {"type": "string", "description": "Nombre, SKU o categoría"},
            },
            "required": ["producto"],
        },
    },
    {
        "name": "calcular_cotizacion",
        "description": (
            "Calcula una cotización: subtotal, descuento, IVA (19%) y fecha de "
            "validez (+15 días). Consulta antes el inventario para usar precios reales."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "descripcion": {"type": "string"},
                            "precio_unitario": {"type": "number"},
                            "cantidad": {"type": "integer"},
                        },
                        "required": ["descripcion", "precio_unitario", "cantidad"],
                    },
                },
                "descuento_pct": {"type": "number", "description": "0 a 100; usa 0 si no aplica"},
            },
            "required": ["items", "descuento_pct"],
        },
    },
    {
        "name": "buscar_conocimiento",
        "description": (
            "Busca en la base de conocimiento interna: viáticos, vacaciones, "
            "staffing, trabajo remoto, horas extra, desempeño, seguridad, "
            "onboarding, capacitación y licencias."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pregunta": {"type": "string", "description": "Pregunta o palabras clave"},
            },
            "required": ["pregunta"],
        },
    },
]


def consultar_inventario(producto: str) -> str:
    inventario = json.loads((DATA_DIR / "inventario.json").read_text(encoding="utf-8"))
    consulta = producto.lower().strip()
    resultados = [
        item
        for item in inventario
        if consulta in item["nombre"].lower()
        or consulta in item["sku"].lower()
        or consulta in item["categoria"].lower()
    ]
    if not resultados:
        return f"Sin resultados para '{producto}'. Categorías: licencias, hardware, servicios, capacitacion."
    return json.dumps(resultados, ensure_ascii=False)


def calcular_cotizacion(items: list[dict], descuento_pct: float) -> str:
    subtotal = sum(i["precio_unitario"] * i["cantidad"] for i in items)
    descuento = subtotal * (descuento_pct / 100)
    neto = subtotal - descuento
    iva = neto * 0.19
    return json.dumps(
        {
            "subtotal_clp": round(subtotal),
            "descuento_clp": round(descuento),
            "neto_clp": round(neto),
            "iva_19_clp": round(iva),
            "total_clp": round(neto + iva),
            "valida_hasta": (date.today() + timedelta(days=15)).isoformat(),
        },
        ensure_ascii=False,
    )


def buscar_conocimiento(pregunta: str) -> str:
    texto = (DATA_DIR / "conocimiento.md").read_text(encoding="utf-8")
    secciones = [s.strip() for s in texto.split("\n## ")[1:]]
    palabras = {p for p in pregunta.lower().split() if len(p) > 3}
    puntaje = lambda s: sum(1 for p in palabras if p in s.lower())
    relevantes = [s for s in sorted(secciones, key=puntaje, reverse=True)[:2] if puntaje(s) > 0]
    if not relevantes:
        return "No se encontró información relevante en la base de conocimiento."
    return "\n\n---\n\n".join(f"## {s}" for s in relevantes)


IMPLEMENTACIONES = {
    "consultar_inventario": consultar_inventario,
    "calcular_cotizacion": calcular_cotizacion,
    "buscar_conocimiento": buscar_conocimiento,
}


def ejecutar_herramienta(nombre: str, entrada: dict) -> str:
    # Los errores vuelven como texto dentro del tool_result: el modelo los lee
    # y puede reintentar con otros argumentos.
    try:
        return IMPLEMENTACIONES[nombre](**entrada)
    except Exception as exc:
        return f"Error al ejecutar {nombre}: {exc}"


def ejecutar_agente(conversacion: list[dict]) -> str:
    for _ in range(MAX_ITERACIONES):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversacion,
        )
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")

        conversacion.append({"role": "assistant", "content": response.content})
        resultados = []
        for bloque in response.content:
            if bloque.type == "tool_use":
                print(f"  [tool] {bloque.name}({json.dumps(bloque.input, ensure_ascii=False)})")
                resultados.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": ejecutar_herramienta(bloque.name, bloque.input),
                    }
                )
        conversacion.append({"role": "user", "content": resultados})

    return "(se alcanzó el límite de iteraciones)"


def main() -> None:
    print("Asistente de Operaciones (CLI) — escribe 'salir' para terminar.")
    print("Prueba: 'cotiza 2 ThinkPad con 10% de descuento' o '¿cómo pido vacaciones?'\n")
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
        conversacion.append({"role": "assistant", "content": respuesta})
        print(f"\nAgente: {respuesta}\n")


if __name__ == "__main__":
    main()
