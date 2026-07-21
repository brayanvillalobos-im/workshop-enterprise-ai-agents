"""Herramientas del Asistente de Operaciones.

Cada herramienta tiene dos mitades que viajan por caminos distintos:

1. La DEFINICIÓN (JSON Schema): es lo único que Claude "ve". Con el nombre,
   la descripción y el schema decide cuándo llamarla y con qué argumentos.
2. La IMPLEMENTACIÓN (función Python): se ejecuta en NUESTRO servidor cuando
   Claude la pide. El modelo nunca ejecuta código aquí — solo solicita.
"""

from __future__ import annotations

import json
from datetime import date, timedelta
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"

# IVA vigente en Chile — en un sistema real vendría de configuración.
IVA = 0.19
DIAS_VALIDEZ_COTIZACION = 15

TOOLS: list[dict] = [
    {
        "name": "consultar_inventario",
        "description": (
            "Busca productos o servicios en el inventario de la consultora por "
            "nombre, SKU o categoría (licencias, hardware, servicios, "
            "capacitacion). Devuelve stock, precio en CLP y SKU. Úsala siempre "
            "que el usuario pregunte por disponibilidad o precios."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "producto": {
                    "type": "string",
                    "description": "Nombre, SKU o categoría a buscar (ej: 'laptop', 'SRV-CELL-FS', 'licencias')",
                }
            },
            "required": ["producto"],
        },
    },
    {
        "name": "calcular_cotizacion",
        "description": (
            "Calcula una cotización formal: subtotal, descuento, IVA (19%) y "
            "fecha de validez (+15 días). Antes de cotizar, consulta el "
            "inventario para usar los precios unitarios reales."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "items": {
                    "type": "array",
                    "description": "Ítems a cotizar",
                    "items": {
                        "type": "object",
                        "properties": {
                            "descripcion": {"type": "string"},
                            "precio_unitario": {"type": "number", "description": "Precio unitario en CLP"},
                            "cantidad": {"type": "integer"},
                        },
                        "required": ["descripcion", "precio_unitario", "cantidad"],
                    },
                },
                "descuento_pct": {
                    "type": "number",
                    "description": "Descuento en porcentaje (0 a 100). Usa 0 si no aplica.",
                },
            },
            "required": ["items", "descuento_pct"],
        },
    },
    {
        "name": "buscar_conocimiento",
        "description": (
            "Busca en la base de conocimiento interna: políticas de viáticos, "
            "vacaciones, staffing, trabajo remoto, horas extra, evaluación de "
            "desempeño, seguridad, onboarding, capacitación y licencias. Úsala "
            "para cualquier pregunta sobre políticas o procesos internos."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "pregunta": {
                    "type": "string",
                    "description": "Pregunta o palabras clave a buscar",
                }
            },
            "required": ["pregunta"],
        },
    },
]


def consultar_inventario(producto: str) -> str:
    # Los participantes editan inventario.json a mano durante el taller: si el
    # formato se rompe, devolvemos una pista clara en vez de un traceback.
    try:
        inventario = json.loads((DATA_DIR / "inventario.json").read_text(encoding="utf-8"))
    except FileNotFoundError:
        return "No encuentro el archivo app/data/inventario.json. ¿Se movió o se borró?"
    except json.JSONDecodeError as exc:
        return (
            f"El archivo inventario.json tiene un error de formato cerca de la "
            f"línea {exc.lineno}. Revisa que no falte (o sobre) una coma, una "
            f"comilla o una llave en esa zona."
        )
    consulta = producto.lower().strip()
    resultados = [
        item
        for item in inventario
        if consulta in item["nombre"].lower()
        or consulta in item["sku"].lower()
        or consulta in item["categoria"].lower()
    ]
    if not resultados:
        return (
            f"No se encontraron productos para '{producto}'. "
            "Categorías disponibles: licencias, hardware, servicios, capacitacion."
        )
    # Devolvemos JSON: a los modelos les resulta más fácil citar datos
    # estructurados que texto libre.
    return json.dumps(resultados, ensure_ascii=False, indent=2)


def calcular_cotizacion(items: list[dict], descuento_pct: float) -> str:
    if not items:
        return "Error: la cotización necesita al menos un ítem."
    if not 0 <= descuento_pct <= 100:
        return "Error: descuento_pct debe estar entre 0 y 100."

    subtotal = sum(i["precio_unitario"] * i["cantidad"] for i in items)
    descuento = subtotal * (descuento_pct / 100)
    neto = subtotal - descuento
    iva = neto * IVA
    total = neto + iva
    validez = date.today() + timedelta(days=DIAS_VALIDEZ_COTIZACION)

    return json.dumps(
        {
            "items": items,
            "subtotal_clp": round(subtotal),
            "descuento_pct": descuento_pct,
            "descuento_clp": round(descuento),
            "neto_clp": round(neto),
            "iva_19_clp": round(iva),
            "total_clp": round(total),
            "valida_hasta": validez.isoformat(),
        },
        ensure_ascii=False,
        indent=2,
    )


def buscar_conocimiento(pregunta: str) -> str:
    try:
        texto = (DATA_DIR / "conocimiento.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        return "No encuentro el archivo app/data/conocimiento.md. ¿Se movió o se borró?"
    # Cada política vive bajo un encabezado "## ...": partimos por sección y
    # puntuamos por coincidencia de palabras clave. Es búsqueda simple a
    # propósito — en producción esto sería un índice o embeddings (RAG).
    secciones = [s.strip() for s in texto.split("\n## ")[1:]]
    palabras = {p for p in pregunta.lower().split() if len(p) > 3}

    def puntaje(seccion: str) -> int:
        contenido = seccion.lower()
        return sum(1 for p in palabras if p in contenido)

    relevantes = sorted(secciones, key=puntaje, reverse=True)[:2]
    relevantes = [s for s in relevantes if puntaje(s) > 0]
    if not relevantes:
        return (
            "No se encontró información relevante. Temas disponibles: viáticos, "
            "vacaciones, staffing, trabajo remoto, horas extra, desempeño, "
            "seguridad, onboarding, capacitación, licencias."
        )
    return "\n\n---\n\n".join(f"## {s}" for s in relevantes)


IMPLEMENTACIONES = {
    "consultar_inventario": consultar_inventario,
    "calcular_cotizacion": calcular_cotizacion,
    "buscar_conocimiento": buscar_conocimiento,
}


def ejecutar_herramienta(nombre: str, entrada: dict) -> str:
    """Despacha una llamada de herramienta y devuelve el resultado como texto.

    Los errores se devuelven como texto (no como excepción): así vuelven a
    Claude dentro del tool_result y el modelo puede corregirse solo.
    """
    if nombre not in IMPLEMENTACIONES:
        return f"Error: herramienta desconocida '{nombre}'."
    try:
        return IMPLEMENTACIONES[nombre](**entrada)
    except Exception as exc:
        return f"Error al ejecutar {nombre}: {exc}"
