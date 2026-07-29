# Deploy en Google Cloud Run (guía principal del taller)

Esta guía asume que **nunca usaste Google Cloud**. Cada comando lleva una
línea explicando qué hace. Al final hay una sección para **borrar todo** y no
dejar costos corriendo.

> 💰 Cloud Run tiene capa gratuita y cobra solo por uso. Revisa los precios
> vigentes en la página oficial: <https://cloud.google.com/run/pricing>
>
> ⚠️ Ojo con la región: la **capa gratuita aplica solo en las regiones de
> EE.UU.** (`us-central1`, `us-east1`, `us-west1`), no en `southamerica-west1`.
> Si quieres costo cero, despliega en `us-central1` a cambio de algo más de
> latencia.

## Prerrequisitos

1. Una cuenta de Google Cloud con facturación habilitada
   (<https://console.cloud.google.com>). **¿No quieres poner tu tarjeta?**
   Lee [`cuenta-sin-tarjeta.md`](cuenta-sin-tarjeta.md): tiene la ruta con
   facturación corporativa y una alternativa sin tarjeta ni facturación.
2. El SDK `gcloud` instalado: <https://cloud.google.com/sdk/docs/install>
3. Tu API key de Anthropic a mano.

## Paso 1 — Autenticarse y crear el proyecto

```bash
# Abre el navegador para iniciar sesión con tu cuenta de Google Cloud
gcloud auth login

# Crea un proyecto nuevo y aislado para el workshop (el ID debe ser único
# a nivel global: cambia "tu-nombre" por algo tuyo)
gcloud projects create workshop-agents-tu-nombre --name="Workshop AI Agents"

# Define ese proyecto como el activo para los siguientes comandos
gcloud config set project workshop-agents-tu-nombre
```

> Si el proyecto nuevo no tiene cuenta de facturación asociada, vincúlala en
> la consola web: *Facturación → Vincular cuenta de facturación*.

## Paso 2 — Habilitar las APIs necesarias

```bash
# Cloud Run (el servicio), Cloud Build (construye la imagen por nosotros),
# Artifact Registry (guarda la imagen) y Secret Manager (guarda la API key)
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com secretmanager.googleapis.com
```

## Paso 3 — Guardar la API key como secreto

La key **nunca** va en el código ni en la imagen Docker: va en Secret Manager
y Cloud Run la inyecta como variable de entorno al arrancar el contenedor.

```bash
# Crea el secreto y carga el valor desde el teclado (pega la key y da Enter;
# en Linux/macOS cierra con Ctrl+D, en Windows con Ctrl+Z y Enter)
gcloud secrets create anthropic-api-key --data-file=-
```

```bash
# Averigua el número de tu proyecto (lo necesita el siguiente comando)
gcloud projects describe workshop-agents-tu-nombre --format="value(projectNumber)"

# Permite que la cuenta de servicio de Cloud Run lea el secreto
# (reemplaza NUMERO por el valor anterior)
gcloud secrets add-iam-policy-binding anthropic-api-key \
  --member="serviceAccount:NUMERO-compute@developer.gserviceaccount.com" \
  --role="roles/secretmanager.secretAccessor"
```

## Paso 4 — Desplegar

Desde la **raíz del repo** (donde está el `Dockerfile`):

```bash
# --source .          → Cloud Build construye la imagen desde el Dockerfile
# --region            → southamerica-west1 es Santiago de Chile (baja latencia,
#                       pero SIN capa gratuita); usa us-central1 para costo cero
# --allow-unauthenticated → la URL queda pública (es una demo)
# --set-secrets       → inyecta el secreto como variable ANTHROPIC_API_KEY
# --set-env-vars      → configura el modelo sin tocar código
gcloud run deploy asistente-operaciones \
  --source . \
  --region southamerica-west1 \
  --allow-unauthenticated \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-env-vars "MODEL=claude-sonnet-4-6"
```

La primera vez preguntará si quieres crear el repositorio de Artifact
Registry: responde **Y**. Al terminar imprime la **Service URL**.

## Paso 5 — Verificar

```bash
# El health check debe responder {"status":"ok","api_key_configured":true}
curl https://TU-SERVICE-URL/health
```

Abre la Service URL en el navegador: deberías ver la UI de chat funcionando.
Para ver los logs del agente (las llamadas `[tool] ...`):

```bash
gcloud run services logs read asistente-operaciones --region southamerica-west1
```

## Paso 6 — Borrar todo (¡importante!)

```bash
# Elimina el servicio de Cloud Run
gcloud run services delete asistente-operaciones --region southamerica-west1

# Elimina el secreto con la API key
gcloud secrets delete anthropic-api-key

# Opción nuclear: eliminar el proyecto completo borra TODO lo anterior
# (imágenes, logs, configuración) y garantiza cero costos residuales
gcloud projects delete workshop-agents-tu-nombre
```

## Problemas frecuentes

| Síntoma | Causa probable | Solución |
|---|---|---|
| `PERMISSION_DENIED` al desplegar | Facturación no vinculada | Vincula la cuenta de facturación al proyecto |
| El contenedor no arranca | Puerto incorrecto | El Dockerfile ya usa `$PORT`; no lo hardcodees |
| `/chat` responde 503 | El secreto no llegó | Revisa el binding IAM del Paso 3 y el `--set-secrets` |
| `gcloud: command not found` | SDK no instalado o no está en el PATH | Reinstala y abre una terminal nueva |
