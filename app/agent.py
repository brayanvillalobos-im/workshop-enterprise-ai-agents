"""Loop agéntico: el corazón del Asistente de Operaciones.

El patrón es siempre el mismo, sin importar cuántas herramientas haya:

    1. Enviar conversación + herramientas a Claude (messages.create).
    2. Si stop_reason == "tool_use": ejecutar lo pedido y devolver los
       resultados como bloques tool_result.
    3. Repetir hasta que Claude responda texto final (o tocar el límite
       de iteraciones, que nos protege de loops infinitos).

Es el mismo core del checkpoint 03, extraído a un módulo para que tanto la
CLI como la API HTTP puedan reutilizarlo.
"""

from __future__ import annotations

import json
import os

import anthropic

from .tools import TOOLS, ejecutar_herramienta

MODEL = os.getenv("MODEL", "claude-sonnet-4-6")
MAX_ITERACIONES = 10

SYSTEM_PROMPT = """\
Eres el "Asistente de Operaciones" de una consultora tecnológica chilena.
Ayudas al equipo interno con tres cosas: consultar el inventario de productos
y servicios, preparar cotizaciones y responder preguntas sobre políticas
internas.

Reglas:
- Usa las herramientas disponibles en vez de inventar datos. Si una búsqueda
  no arroja resultados, dilo honestamente.
- Para cotizar, consulta primero el inventario y usa los precios reales.
- Los montos están en pesos chilenos (CLP); formatéalos con separador de miles.
- Responde en español, de forma breve y profesional.
"""


def ejecutar_agente(
    messages: list[dict],
    client: anthropic.Anthropic,
) -> tuple[str, list[str]]:
    """Corre el loop agéntico sobre un historial completo de conversación.

    El servidor es stateless: quien llama envía TODO el historial y recibe
    solo la respuesta final más la lista de herramientas usadas (para la UI).
    """
    conversacion = list(messages)
    herramientas_usadas: list[str] = []

    for _ in range(MAX_ITERACIONES):
        response = client.messages.create(
            model=MODEL,
            max_tokens=2048,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=conversacion,
        )

        if response.stop_reason != "tool_use":
            # Claude terminó: juntamos los bloques de texto y salimos del loop.
            texto = "".join(b.text for b in response.content if b.type == "text")
            return texto, herramientas_usadas

        # Claude pidió una o más herramientas. Primero guardamos SU turno
        # completo (incluye los bloques tool_use con sus IDs)...
        conversacion.append({"role": "assistant", "content": response.content})

        # ...y luego ejecutamos cada solicitud y devolvemos los resultados en
        # UN solo mensaje de usuario (la API exige un tool_result por cada
        # tool_use, emparejados por ID).
        resultados = []
        for bloque in response.content:
            if bloque.type == "tool_use":
                print(
                    f"[tool] {bloque.name}({json.dumps(bloque.input, ensure_ascii=False)})",
                    flush=True,
                )
                herramientas_usadas.append(bloque.name)
                resultado = ejecutar_herramienta(bloque.name, bloque.input)
                resultados.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": bloque.id,
                        "content": resultado,
                    }
                )
        conversacion.append({"role": "user", "content": resultados})

    return (
        "Alcancé el límite de pasos para esta consulta. Intenta dividirla en "
        "preguntas más simples.",
        herramientas_usadas,
    )
