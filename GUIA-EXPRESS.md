# ⚡ Guía Express del participante

**No necesitas saber programar.** Esta guía es la ruta completa de las 2
sesiones: comandos numerados para copiar y pegar, con el resultado esperado de
cada uno. Si algo falla, busca el mensaje en el
[Troubleshooting del README](README.md#troubleshooting) o levanta la mano 🙋.

> 💡 Los comandos se pegan en la **terminal**: en Windows usa *PowerShell*;
> en macOS/Linux, *Terminal*. Todos se ejecutan desde la carpeta del repo.

---

## Sesión 1 — Tu agente corriendo y personalizado (75 min)

### Parte A — Puesta en marcha (~20 min)

**1. Verifica Python** (necesitas 3.10 o superior):

```bash
python --version
```
✅ Esperado: `Python 3.10.x` o superior. Si dice 3.9 o da error, avisa al facilitador.

**2. Descarga el repo y entra a la carpeta:**

```bash
git clone https://github.com/brayanvillalobos-im/workshop-enterprise-ai-agents.git
cd workshop-enterprise-ai-agents
```
✅ Esperado: termina sin errores y tu terminal queda "dentro" de la carpeta.

**3. Crea el entorno aislado de Python** (una cajita donde viven las dependencias):

```bash
python -m venv .venv
```
✅ Esperado: no imprime nada (eso es bueno) y aparece una carpeta `.venv`.

**4. Activa el entorno:**

```bash
# Windows (PowerShell):
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate
```
✅ Esperado: el prompt de la terminal ahora empieza con `(.venv)`.

> ⚠️ Si PowerShell dice *"running scripts is disabled"*, ejecuta
> `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` y reintenta.

**5. Instala las dependencias:**

```bash
pip install -r requirements.txt
```
✅ Esperado: varias líneas de descarga y al final `Successfully installed anthropic-... fastapi-...`.

**6. Configura tu API key** (te la entrega el facilitador):

```bash
# Windows:
copy .env.example .env

# macOS / Linux:
cp .env.example .env
```
Luego abre el archivo `.env` con el Bloc de notas / TextEdit / VS Code y
reemplaza `sk-ant-...` por tu key real. Guarda el archivo.

✅ Esperado: el archivo `.env` tiene una línea `ANTHROPIC_API_KEY=sk-ant-` seguida de tu key completa, sin comillas ni espacios.

**7. Prueba de humo — tu primera llamada a Claude:**

```bash
python checkpoints/00-hola-claude/main.py
```
✅ Esperado: Claude se presenta y explica qué es un agente de IA, en español.
❌ Si dice `Falta ANTHROPIC_API_KEY`: revisa el paso 6.

### Parte B — El agente completo en tu navegador (~20 min)

**8. Levanta el servidor del agente:**

```bash
uvicorn app.main:app --reload
```
✅ Esperado: varias líneas y al final `Uvicorn running on http://127.0.0.1:8000`.
La terminal queda "ocupada" — es normal, el servidor está vivo. Para
apagarlo más tarde: `Ctrl+C`.

**9. Abre el agente:** ve a <http://127.0.0.1:8000> en tu navegador.

✅ Esperado: la interfaz de chat del "Asistente de Operaciones".

**10. Conversa con tu agente.** Prueba estas tres (una por una) y observa los
badges 🔧 que muestran qué herramienta usó:

- `¿qué laptops tenemos y cuánto cuestan?` → badge `consultar_inventario`
- `cotízame 2 ThinkPad con 10% de descuento` → badges `consultar_inventario` + `calcular_cotizacion`
- `¿cuál es la política de trabajo remoto?` → badge `buscar_conocimiento`

También puedes mirar la terminal: cada `[tool] ...` es el agente usando una
herramienta en vivo.

### Parte C — Personaliza tu agente SIN programar (~30 min)

Los tres archivos de esta parte se editan con cualquier editor de texto.
**No hace falta reiniciar el servidor**: guarda el archivo y envía otro
mensaje en el chat.

**11. Cambia la personalidad** — abre [`app/config/system_prompt.txt`](app/config/system_prompt.txt):

Ideas: que responda como pirata, que sea ultra formal, que salude siempre con
tu nombre, que responda en inglés, que las cotizaciones incluyan siempre una
recomendación. Guarda y pregunta cualquier cosa en el chat.

✅ Esperado: el agente cambia de personalidad en la siguiente respuesta.

**12. Vende tus propios productos** — abre [`app/data/inventario.json`](app/data/inventario.json):

Cambia nombres, precios o stock, o copia un bloque `{...},` para agregar un
producto nuevo. Respeta las comas y comillas (si rompes el formato, el agente
te lo dirá amablemente en el chat).

✅ Esperado: pregunta por tu producto nuevo y el agente lo encuentra.

**13. Escribe tus propias políticas** — abre [`app/data/conocimiento.md`](app/data/conocimiento.md):

Cada política es una sección que empieza con `## Título`. Agrega una tuya
(ej: `## Política de mascotas en la oficina`) con 2-3 líneas de texto.

✅ Esperado: pregúntale al agente por tu política nueva y te la responde.

---

## Sesión 2 — Tu agente en internet (75 min)

Hoy el agente sale de tu computador y queda en una URL pública usando
**Google Cloud Run**. Hay dos caminos:

- 🤖 **Con Claude Code** (el que hacemos en vivo): un solo prompt y Claude
  ejecuta todos los comandos de `gcloud` por ti, explicando cada paso. El
  prompt está en [`deploy/00-deploy-con-claude.md`](deploy/00-deploy-con-claude.md).
- ✋ **A mano**, comando por comando: [`deploy/01-cloud-run.md`](deploy/01-cloud-run.md).

> 💳 **¿Te preocupa poner una tarjeta?** Es la duda más común y tiene
> respuesta: [`deploy/cuenta-sin-tarjeta.md`](deploy/cuenta-sin-tarjeta.md).
> En el taller usamos la facturación corporativa (nadie expone su tarjeta), y
> ahí está también la alternativa gratuita sin ningún medio de pago.

Esta es la vista de pájaro del camino manual (útil para entender qué hace
Claude cuando lo automatiza):

**1. Inicia sesión en Google Cloud:** `gcloud auth login`
✅ Esperado: se abre el navegador y al volver dice `You are now logged in`.

**2. Crea y selecciona el proyecto del taller** (pasos 1 de la guía).
✅ Esperado: `gcloud config list` muestra tu proyecto.

**3. Habilita las APIs** (paso 2 de la guía).
✅ Esperado: `Operation ... finished successfully`.

**4. Guarda tu API key como secreto** (paso 3 de la guía) — la key viaja a la
bóveda de Google, nunca al código.
✅ Esperado: `Created version [1] of the secret [anthropic-api-key]`.

**5. Despliega** (paso 4 de la guía): `gcloud run deploy ...`
✅ Esperado: tras ~3-5 min, una línea `Service URL: https://asistente-operaciones-...run.app`.

**6. Compártelo:** abre la Service URL en tu teléfono 📱 y muéstrale tu agente
a quien quieras.

**7. MUY IMPORTANTE — borra todo al final** (paso 6 de la guía) para no dejar
costos corriendo.
✅ Esperado: `Deleted service [asistente-operaciones]`.

---

## ¿Quieres ver cómo funciona por dentro? (opcional)

Si programas (o te da curiosidad), la carpeta [`checkpoints/`](checkpoints/)
reconstruye el agente en 4 pasos, del "hola mundo" al agente completo. Cada
carpeta tiene su README. Es el material extendido de la Sesión 1 — no es
necesario para el taller.
