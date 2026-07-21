"""API HTTP del Asistente de Operaciones (Sesión 2 del workshop).

Arquitectura:

    Navegador (static/index.html)  ->  FastAPI (/chat)  ->  API de Anthropic

La API key vive SOLO en el servidor (variable de entorno o secreto de la
nube). El navegador nunca la ve: habla únicamente con este backend.

Correr en local:  uvicorn app.main:app --reload
"""

from __future__ import annotations

import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .agent import MODEL, ejecutar_agente

load_dotenv()

STATIC_DIR = Path(__file__).parent / "static"

app = FastAPI(title="Asistente de Operaciones", version="1.0.0")

# Validamos la key al importar el módulo: un error claro al arrancar es mejor
# que un traceback críptico en la primera request.
API_KEY = os.getenv("ANTHROPIC_API_KEY")
if not API_KEY:
    print("=" * 70)
    print("ADVERTENCIA: falta la variable de entorno ANTHROPIC_API_KEY.")
    print("El servidor arranca, pero /chat respondera 503 hasta configurarla.")
    print("Solucion: copia .env.example a .env y agrega tu API key.")
    print("=" * 70)

client: anthropic.Anthropic | None = anthropic.Anthropic() if API_KEY else None


class ChatRequest(BaseModel):
    # El servidor es stateless: el navegador envía el historial completo
    # [{"role": "user"|"assistant", "content": "..."}] en cada request.
    messages: list[dict]


class ChatResponse(BaseModel):
    reply: str
    tool_calls: list[str]  # nombres de herramientas usadas (badges en la UI)


@app.get("/")
def index() -> FileResponse:
    """Sirve la UI de chat."""
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/health")
def health() -> dict:
    """Endpoint de salud: lo usan las nubes para saber si el contenedor vive."""
    return {"status": "ok", "model": MODEL, "api_key_configured": client is not None}


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest) -> ChatResponse:
    if client is None:
        raise HTTPException(
            status_code=503,
            detail="El servidor no tiene configurada ANTHROPIC_API_KEY.",
        )
    if not req.messages:
        raise HTTPException(status_code=400, detail="'messages' no puede estar vacío.")

    # Convertimos errores del SDK en respuestas HTTP limpias: el navegador
    # recibe un mensaje accionable, nunca un traceback.
    try:
        reply, tool_calls = ejecutar_agente(req.messages, client)
    except anthropic.AuthenticationError:
        raise HTTPException(status_code=502, detail="API key inválida o revocada.")
    except anthropic.RateLimitError:
        raise HTTPException(
            status_code=429,
            detail="Límite de peticiones alcanzado. Espera unos segundos y reintenta.",
        )
    except anthropic.APIStatusError as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Error de la API de Anthropic ({exc.status_code}): {exc.message}",
        )
    except anthropic.APIConnectionError:
        raise HTTPException(
            status_code=502,
            detail="No se pudo conectar con la API de Anthropic. Revisa tu red.",
        )

    return ChatResponse(reply=reply, tool_calls=tool_calls)
