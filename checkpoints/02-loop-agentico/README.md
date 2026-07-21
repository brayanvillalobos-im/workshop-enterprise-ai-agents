# Checkpoint 02 — El loop agéntico

> 📚 Material opcional para quienes programan — no es necesario para seguir
> el taller (la ruta principal está en [GUIA-EXPRESS.md](../../GUIA-EXPRESS.md)).

## Objetivo
Cerrar el ciclo que quedó abierto en el checkpoint 01: ejecutar la herramienta
que Claude pide, devolverle el resultado y dejarlo continuar hasta la
respuesta final.

## Concepto que enseña
El **loop agéntico**, el patrón detrás de todo agente de IA:

```
mientras stop_reason == "tool_use":
    1. guardar el turno del assistant (con sus bloques tool_use)
    2. ejecutar cada herramienta solicitada
    3. responder con bloques tool_result (emparejados por tool_use_id)
volver a llamar al modelo → respuesta final
```

Dos detalles que siempre causan bugs en producción y aquí se ven claros:
el **límite de iteraciones** (protección contra ciclos infinitos) y que los
`tool_result` van todos juntos **en un solo mensaje de usuario**.

## Cómo correrlo
```bash
python checkpoints/02-loop-agentico/main.py
```
Prueba: `¿cuánto costarían 3 laptops Lenovo y 100 horas de célula full-stack?`
— verás al agente encadenar varias llamadas a la herramienta él solo.

## Ejercicio opcional
Baja `MAX_ITERACIONES` a 1 y haz una pregunta que requiera dos búsquedas.
Observa cómo se corta. ¿Por qué un límite muy bajo rompe al agente y uno muy
alto es un riesgo de costos?
