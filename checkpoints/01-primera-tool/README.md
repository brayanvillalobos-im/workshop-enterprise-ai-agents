# Checkpoint 01 — Primera herramienta (sin loop)

> 📚 Material opcional para quienes programan — no es necesario para seguir
> el taller (la ruta principal está en [GUIA-EXPRESS.md](../../GUIA-EXPRESS.md)).

## Objetivo
Definir una herramienta y ver qué pasa cuando Claude decide usarla.

## Concepto que enseña
**Claude no ejecuta código: lo solicita.** Al pasar `tools` a la llamada, el
modelo puede responder con `stop_reason == "tool_use"` y un bloque que dice
*qué* herramienta quiere y *con qué* argumentos (validados contra tu JSON
Schema). La conversación queda en pausa hasta que tu código ejecute la
herramienta y devuelva el resultado. Este script se detiene ahí a propósito
para que la pausa sea visible.

## Cómo correrlo
```bash
python checkpoints/01-primera-tool/main.py
```

## Ejercicio opcional
Cambia la pregunta a algo que no necesite inventario ("¿qué es Docker?") y
vuelve a correr. Verás `stop_reason == "end_turn"`: el modelo decide **solo**
cuándo una herramienta es necesaria — esa autonomía es la esencia de un agente.
