# Deploy en Azure Container Apps (equivalente Azure)

El mismo agente en Azure: **ACR** construye y guarda la imagen, **Key Vault**
guarda la API key y **Container Apps** ejecuta el contenedor serverless.
Requiere el [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli).

> 💰 Precios vigentes: <https://azure.microsoft.com/pricing/details/container-apps/>

## Paso 1 — Autenticarse y preparar

```bash
# Inicia sesión (abre el navegador)
az login

# Instala la extensión de Container Apps
az extension add --name containerapp --upgrade

# Todo el workshop vive en un solo grupo de recursos: borrarlo al final
# elimina todo de una vez
az group create --name rg-workshop-agents --location eastus
```

## Paso 2 — Construir la imagen en ACR

```bash
# Crea el registro (el nombre debe ser único global y sin guiones)
az acr create --resource-group rg-workshop-agents \
  --name acrworkshopTUNOMBRE --sku Basic

# ACR construye la imagen EN LA NUBE desde tu carpeta local (no necesitas
# Docker instalado). Ejecutar desde la raíz del repo:
az acr build --registry acrworkshopTUNOMBRE \
  --image asistente-operaciones:v1 .
```

## Paso 3 — Guardar la API key en Key Vault

```bash
# Crea el vault (nombre único global)
az keyvault create --resource-group rg-workshop-agents \
  --name kv-workshop-TUNOMBRE --location eastus

# Guarda la key como secreto
az keyvault secret set --vault-name kv-workshop-TUNOMBRE \
  --name anthropic-api-key --value "sk-ant-TU-KEY"
```

## Paso 4 — Crear la Container App

```bash
# El "environment" es la red/cluster compartido donde viven las apps
az containerapp env create --resource-group rg-workshop-agents \
  --name env-workshop --location eastus

# Crea la app con identidad administrada (para leer Key Vault sin passwords),
# ingress público en el puerto 8080 y registro ACR conectado
az containerapp create --resource-group rg-workshop-agents \
  --name asistente-operaciones \
  --environment env-workshop \
  --image acrworkshopTUNOMBRE.azurecr.io/asistente-operaciones:v1 \
  --registry-server acrworkshopTUNOMBRE.azurecr.io \
  --registry-identity system \
  --system-assigned \
  --ingress external --target-port 8080 \
  --env-vars MODEL=claude-sonnet-4-6

# Autoriza a la identidad de la app a leer secretos del vault
# (PRINCIPAL_ID sale del comando siguiente)
az containerapp show --resource-group rg-workshop-agents \
  --name asistente-operaciones --query identity.principalId -o tsv

az keyvault set-policy --name kv-workshop-TUNOMBRE \
  --object-id PRINCIPAL_ID --secret-permissions get

# Conecta el secreto de Key Vault y expónlo como variable de entorno
az containerapp secret set --resource-group rg-workshop-agents \
  --name asistente-operaciones \
  --secrets "anthropic-key=keyvaultref:https://kv-workshop-TUNOMBRE.vault.azure.net/secrets/anthropic-api-key,identityref:system"

az containerapp update --resource-group rg-workshop-agents \
  --name asistente-operaciones \
  --set-env-vars "ANTHROPIC_API_KEY=secretref:anthropic-key"
```

## Paso 5 — Verificar y borrar

```bash
# Obtén la URL pública
az containerapp show --resource-group rg-workshop-agents \
  --name asistente-operaciones --query properties.configuration.ingress.fqdn -o tsv

curl https://TU-FQDN/health

# Al terminar: borrar el grupo de recursos elimina TODO (app, ACR, vault)
az group delete --name rg-workshop-agents --yes
```
