# Checkpoint 03 — Agente completo

## Objetivo
Armar el "Asistente de Operaciones" completo en una CLI: 3 herramientas,
system prompt y el mismo loop del checkpoint 02.

## Concepto que enseña
Dos cosas nuevas sobre el loop que ya conoces:

1. **El system prompt convierte un modelo en un agente**: define rol, reglas
   de negocio (usar precios reales, no inventar datos) y tono. Compara las
   respuestas con y sin él.
2. **Orquestación entre herramientas**: pide una cotización y observa cómo el
   modelo decide solo la secuencia `consultar_inventario` →
   `calcular_cotizacion`, pasando los precios de una a otra. Nadie programó
   ese flujo: emerge de las descripciones de las herramientas.

Este archivo es el "final" de la Sesión 1. La carpeta `app/` contiene el mismo
núcleo separado en módulos (`agent.py`, `tools.py`) y expuesto como API HTTP —
ese salto es el inicio de la Sesión 2.

## Cómo correrlo
```bash
python checkpoints/03-agente-completo/main.py
```
Pruebas sugeridas:
- `¿qué laptops tenemos y cuánto cuestan?`
- `cotízame 3 ThinkPad y 200 horas de célula de datos con 5% de descuento`
- `¿cuál es la política de trabajo remoto?`

## Ejercicio opcional
Agrega una cuarta herramienta `crear_ticket(titulo, descripcion)` que solo
imprima el ticket por consola y devuelva un ID inventado. Necesitas tocar dos
lugares: `TOOLS` (definición) e `IMPLEMENTACIONES` (implementación). Luego
pídele al agente "crea un ticket para pedir una laptop nueva".
