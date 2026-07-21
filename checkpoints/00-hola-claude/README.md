# Checkpoint 00 — Hola Claude

> 📚 Material opcional para quienes programan — no es necesario para seguir
> el taller (la ruta principal está en [GUIA-EXPRESS.md](../../GUIA-EXPRESS.md)).

## Objetivo
Hacer tu primera llamada al API de Anthropic y verificar que el entorno quedó
bien configurado.

## Concepto que enseña
La unidad básica de todo: `client.messages.create()`. Una conversación es una
lista de mensajes con `role` y `content`, y la respuesta llega como **bloques
de contenido** (no como un string plano). Todo lo que viene después — tools,
loop, API web — se construye sobre esta misma llamada.

## Cómo correrlo
```bash
# desde la raíz del repo, con el venv activado y .env configurado
python checkpoints/00-hola-claude/main.py
```

## Ejercicio opcional
Agrega el parámetro `system="Responde siempre en verso"` a la llamada y
observa cómo cambia la respuesta. El *system prompt* define la personalidad
del agente y será clave en el checkpoint 03.
