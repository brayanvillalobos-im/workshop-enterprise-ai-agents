# Enterprise AI Agents

### Arquitectura y Despliegue de Agentes de IA en la Nube Corporativa

Workshop interno de **Imagemaker** · 2 sesiones · Facilitador: **Brayan Villalobos**, Technical Manager

Construiremos desde cero un agente de IA — el **"Asistente de Operaciones"** —
con el SDK de Python de Anthropic, y lo desplegaremos como contenedor
serverless en la nube. Sin frameworks mágicos: el objetivo es entender **el
patrón agéntico** que está debajo de todos ellos.

---

## Índice

1. [Prerrequisitos](#prerrequisitos)
2. [Setup en 5 pasos](#setup-en-5-pasos)
3. [Sesión 1 — Mapa de checkpoints](#sesión-1--mapa-de-checkpoints)
4. [Sesión 2 — La app final](#sesión-2--la-app-final)
5. [Guías de deploy](#guías-de-deploy)
6. [Equivalencias multi-cloud](#equivalencias-multi-cloud)
7. [Troubleshooting](#troubleshooting)

---

## Prerrequisitos

- **Python 3.10 o superior** (`python --version` para verificar).
- Una **API key de Anthropic** (el facilitador entrega keys del workspace del
  taller; si usas la tuya: <https://platform.claude.com/>).
- **Docker Desktop** (solo Sesión 2, para probar la imagen en local).
- Cuenta en al menos una nube (Google Cloud recomendada para la Sesión 2).
- Editor de código (VS Code o similar).

No se asume experiencia previa en cloud ni con el API de Anthropic.

## Setup en 5 pasos

```bash
# 1. Clona el repo
git clone https://github.com/brayanvillalobos-im/workshop-enterprise-ai-agents.git
cd workshop-enterprise-ai-agents

# 2. Crea y activa un entorno virtual
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Instala las dependencias
pip install -r requirements.txt

# 4. Configura tu API key
# Copia .env.example a .env y pega tu key en ANTHROPIC_API_KEY
# Windows:            copy .env.example .env
# macOS / Linux:      cp .env.example .env

# 5. Verifica que todo funciona
python checkpoints/00-hola-claude/main.py
```

Si el paso 5 imprime una respuesta de Claude, estás listo. Si no, revisa
[Troubleshooting](#troubleshooting).

## Sesión 1 — Mapa de checkpoints

Cada checkpoint es una carpeta autoejecutable con su propio README. La idea es
avanzar en orden: cada uno agrega **un** concepto sobre el anterior.

| Checkpoint | Concepto que enseña |
|---|---|
| [`00-hola-claude`](checkpoints/00-hola-claude/) | La llamada básica: `messages.create`, roles y bloques de contenido |
| [`01-primera-tool`](checkpoints/01-primera-tool/) | Tools y JSON Schema: Claude **solicita**, no ejecuta (`stop_reason == "tool_use"`) |
| [`02-loop-agentico`](checkpoints/02-loop-agentico/) | El loop agéntico: ejecutar → `tool_result` → repetir, con límite de iteraciones |
| [`03-agente-completo`](checkpoints/03-agente-completo/) | System prompt + 3 herramientas: orquestación que **emerge**, nadie la programa |

## Sesión 2 — La app final

La carpeta [`app/`](app/) contiene el mismo agente del checkpoint 03,
reorganizado para producción:

- [`agent.py`](app/agent.py) — el loop agéntico, ahora reutilizable.
- [`tools.py`](app/tools.py) — definiciones (JSON Schema) + implementaciones.
- [`main.py`](app/main.py) — FastAPI: `POST /chat` (stateless), `GET /` (UI), `GET /health`.
- [`static/index.html`](app/static/index.html) — UI de chat vanilla con badges de herramientas.

**Correr en local:**

```bash
uvicorn app.main:app --reload
# abre http://127.0.0.1:8000
```

**Probar la imagen Docker en local:**

```bash
docker build -t asistente-operaciones .
docker run -p 8080:8080 --env-file .env asistente-operaciones
# abre http://localhost:8080
```

> 🔑 Detalle de arquitectura importante: el navegador **nunca** ve la API key.
> Solo habla con FastAPI, y FastAPI habla con Anthropic. Ese es el motivo de
> tener un backend aunque la UI sea estática.

## Guías de deploy

| Guía | Nube | Nivel de detalle |
|---|---|---|
| [`deploy/01-cloud-run.md`](deploy/01-cloud-run.md) | Google Cloud Run | ⭐ Guía principal del taller, comando a comando |
| [`deploy/02-aws-app-runner.md`](deploy/02-aws-app-runner.md) | AWS App Runner | Resumida pero completa |
| [`deploy/03-azure-container-apps.md`](deploy/03-azure-container-apps.md) | Azure Container Apps | Resumida pero completa |
| [`deploy/multi-cloud.md`](deploy/multi-cloud.md) | Bedrock / Vertex AI | El mismo agente con modelos gestionados en la nube del cliente |

## Equivalencias multi-cloud

La tabla que conviene tener en la cabeza al hablar con clientes:

| Concepto | GCP | AWS | Azure |
|---|---|---|---|
| Contenedor serverless | Cloud Run | App Runner | Container Apps |
| Secretos | Secret Manager | Secrets Manager | Key Vault |
| Registro de imágenes | Artifact Registry | ECR | ACR |
| Modelos gestionados (Claude) | Vertex AI | Amazon Bedrock | Microsoft Foundry |

## Troubleshooting

**1. `authentication_error` / HTTP 401 — API key inválida**
La key está mal copiada, tiene espacios o fue revocada. Revisa que `.env`
tenga la línea completa `ANTHROPIC_API_KEY=sk-ant-...` sin comillas y vuelve a
activar el venv. Verifica la key en <https://platform.claude.com/>.

**2. Errores de sintaxis raros (`TypeError: unsupported operand ... | ...`)**
Estás usando Python < 3.10. Verifica con `python --version`; en Windows a
veces `python` apunta a una versión vieja — prueba `py -3.12` o reinstala
desde <https://python.org>.

**3. `[Errno 10048] address already in use` — puerto ocupado**
Otro proceso usa el 8000/8080 (otro uvicorn, Docker, etc.). Levanta en otro
puerto: `uvicorn app.main:app --reload --port 8001`, o cierra el proceso
anterior.

**4. `pip install` falla con error SSL (`CERTIFICATE_VERIFY_FAILED`)**
Típico detrás de proxys corporativos. Opciones: conéctate fuera de la VPN, o
instala confiando en los hosts de PyPI:
`pip install -r requirements.txt --trusted-host pypi.org --trusted-host files.pythonhosted.org`
(solo para el taller; en producción configura el certificado del proxy).

**5. `gcloud` pide credenciales o responde `PERMISSION_DENIED`**
No has iniciado sesión o el proyecto activo no es el correcto. Ejecuta
`gcloud auth login`, luego `gcloud config set project TU-PROYECTO` y verifica
con `gcloud config list`.

---

## Licencia y datos

Material interno de Imagemaker para fines de capacitación. Todos los datos de
`app/data/` (inventario, políticas) son **ficticios**.
