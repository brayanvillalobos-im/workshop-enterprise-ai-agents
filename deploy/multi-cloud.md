# Multi-cloud: el mismo agente en la nube del cliente

Un escenario común en consultoría: el cliente no puede (o no quiere) llamar
directo al API de Anthropic — necesita que la inferencia corra dentro de su
contrato cloud (facturación, compliance, data residency). Claude está
disponible como **modelo gestionado** en las tres nubes, y el SDK de Python
lo resuelve **cambiando solo el cliente**: el loop agéntico, las herramientas
y el system prompt quedan idénticos.

| Nube | Servicio | Cliente del SDK | Model ID |
|---|---|---|---|
| API directa | Claude API | `Anthropic()` | `claude-sonnet-4-6` |
| AWS | Amazon Bedrock | `AnthropicBedrockMantle()` | `anthropic.claude-sonnet-4-6` (prefijo `anthropic.`) |
| GCP | Vertex AI | `AnthropicVertex()` | `claude-sonnet-4-6` (sin prefijo) |
| Azure | Microsoft Foundry | `AnthropicFoundry()` | `claude-sonnet-4-6` |

## Amazon Bedrock

```bash
pip install "anthropic[bedrock]"
```

```python
from anthropic import AnthropicBedrockMantle

# Usa las credenciales AWS estándar del entorno (aws configure, roles IAM,
# variables AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY). No hay API key de
# Anthropic: la facturación va por AWS.
client = AnthropicBedrockMantle(aws_region="us-east-1")

response = client.messages.create(
    model="anthropic.claude-sonnet-4-6",  # en Bedrock el ID lleva prefijo
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hola"}],
)
```

> Antes de usarlo, habilita el acceso al modelo en la consola de Bedrock
> (*Model access*) en la región elegida.

## Google Vertex AI

```bash
pip install "anthropic[vertex]"
```

```python
from anthropic import AnthropicVertex

# Autenticación por Application Default Credentials de GCP:
#   gcloud auth application-default login
client = AnthropicVertex(project_id="mi-proyecto-gcp", region="global")

response = client.messages.create(
    model="claude-sonnet-4-6",  # en Vertex el ID va sin prefijo
    max_tokens=1024,
    messages=[{"role": "user", "content": "Hola"}],
)
```

> Habilita el modelo en Vertex AI Model Garden del proyecto. `region="global"`
> es lo recomendado; también acepta regiones específicas.

## Adaptar nuestro agente

En `app/main.py` el cliente se crea una sola vez. Para hacerlo multi-cloud,
reemplaza esa línea por una pequeña fábrica controlada por variable de entorno:

```python
import os

def crear_cliente():
    proveedor = os.getenv("LLM_PROVIDER", "anthropic")
    if proveedor == "bedrock":
        from anthropic import AnthropicBedrockMantle
        return AnthropicBedrockMantle(aws_region=os.environ["AWS_REGION"])
    if proveedor == "vertex":
        from anthropic import AnthropicVertex
        return AnthropicVertex(
            project_id=os.environ["GCP_PROJECT"],
            region=os.getenv("GCP_REGION", "global"),
        )
    from anthropic import Anthropic
    return Anthropic()  # API directa (default)
```

Y ajusta `MODEL` según la nube (recuerda el prefijo `anthropic.` en Bedrock).
**Nada más cambia**: `messages.create`, `tools`, `stop_reason`, el loop — todo
es la misma interfaz.

## Puntos para la discusión del taller

- **Disponibilidad de features**: las nubes de terceros van detrás del API
  directo en features nuevas (por ejemplo, algunas herramientas server-side
  no están en Bedrock/Vertex). Verifica la matriz oficial:
  <https://platform.claude.com/docs/en/api/claude-on-vertex-ai> y
  <https://platform.claude.com/docs/en/api/claude-on-amazon-bedrock>
- **Precios**: cada plataforma publica los suyos — no asumas paridad:
  Bedrock (<https://aws.amazon.com/bedrock/pricing/>),
  Vertex AI (<https://cloud.google.com/vertex-ai/generative-ai/pricing>),
  API directa (<https://platform.claude.com/docs/en/pricing>).
- **Credenciales**: en Bedrock/Vertex desaparece la API key de Anthropic; la
  autenticación es la nativa de la nube (IAM/ADC), lo que suele simplificar
  el compliance del cliente.
