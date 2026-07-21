# Deploy en AWS App Runner (equivalente AWS)

El mismo agente, ahora en AWS: **ECR** guarda la imagen, **Secrets Manager**
guarda la API key y **App Runner** ejecuta el contenedor serverless. Guía
resumida pero completa; requiere el [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)
y Docker instalados.

> 💰 A diferencia de Cloud Run, App Runner cobra también por instancias en
> pausa. Precios vigentes: <https://aws.amazon.com/apprunner/pricing/>

## Paso 1 — Autenticarse

```bash
# Configura credenciales (Access Key, Secret, región — ej: us-east-1)
aws configure
```

## Paso 2 — Subir la imagen a ECR

```bash
# Crea el repositorio de imágenes
aws ecr create-repository --repository-name asistente-operaciones

# Averigua tu Account ID (lo usan los comandos siguientes)
aws sts get-caller-identity --query Account --output text

# Autentica Docker contra ECR (reemplaza ACCOUNT y la región si cambia)
aws ecr get-login-password --region us-east-1 | docker login \
  --username AWS --password-stdin ACCOUNT.dkr.ecr.us-east-1.amazonaws.com

# Construye la imagen desde la raíz del repo y súbela
docker build -t asistente-operaciones .
docker tag asistente-operaciones:latest ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/asistente-operaciones:latest
docker push ACCOUNT.dkr.ecr.us-east-1.amazonaws.com/asistente-operaciones:latest
```

## Paso 3 — Guardar la API key en Secrets Manager

```bash
# Crea el secreto (guarda el ARN que devuelve — se usa en el Paso 5)
aws secretsmanager create-secret \
  --name workshop/anthropic-api-key \
  --secret-string "sk-ant-TU-KEY"
```

## Paso 4 — Roles IAM

App Runner necesita dos permisos: **leer la imagen** de ECR y **leer el
secreto**. Lo más simple para el workshop es hacerlo desde la consola web en
el Paso 5 (App Runner crea el rol de acceso a ECR automáticamente). Para el
secreto, crea un rol de instancia con la política `SecretsManagerReadWrite`
acotada a tu secreto (o usa la consola, que lo guía).

## Paso 5 — Crear el servicio

En la consola web (<https://console.aws.amazon.com/apprunner>) — más simple
para quien recién empieza:

1. **Create service** → Source: *Container registry* → elige tu imagen de ECR.
2. Deployment: *Manual*. Access role: deja que la consola cree uno nuevo.
3. Port: `8080`.
4. En **Environment variables**:
   - `MODEL` = `claude-sonnet-4-6` (texto plano)
   - `ANTHROPIC_API_KEY` = referencia a Secrets Manager, pegando el ARN del
     Paso 3 (tipo *Secret*).
5. Instance role: el rol con lectura del secreto (Paso 4).
6. **Create & deploy** y espera ~5 minutos.

## Paso 6 — Verificar y borrar

```bash
# La Default domain aparece en la consola; verifica el health check
curl https://TU-DOMINIO.awsapprunner.com/health

# Al terminar el taller, borra todo para no dejar costos:
aws apprunner delete-service --service-arn ARN-DEL-SERVICIO
aws secretsmanager delete-secret --secret-id workshop/anthropic-api-key --force-delete-without-recovery
aws ecr delete-repository --repository-name asistente-operaciones --force
```
