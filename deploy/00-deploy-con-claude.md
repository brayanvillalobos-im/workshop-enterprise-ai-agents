# 🤖 Deploy en vivo: que Claude despliegue todo en GCP

La demo estrella de la Sesión 2. En vez de que los participantes copien 15
comandos de `gcloud`, **le pedimos a Claude Code que haga el despliegue
completo** y vamos narrando lo que hace. El resultado es una URL pública en
~10 minutos.

> 💡 Idea pedagógica: los participantes ya vieron al agente usar *sus*
> herramientas (inventario, cotizaciones). Ahora ven a **Claude Code usando la
> CLI de gcloud como herramienta**. Es el mismo patrón agéntico, un nivel más
> arriba — y es el cierre natural del taller.

---

## 1. Checklist del facilitador (hacer ANTES de la sesión)

Estos tres pasos requieren un navegador o permisos, así que no conviene
dejarlos para el momento en vivo:

```bash
gcloud auth login
```
✅ Abre el navegador. Al volver debe decir `You are now logged in as [...]`.

```bash
gcloud billing accounts list
```
✅ Debe listar al menos una cuenta `OPEN: True`. Si sale vacío, **pídele a TI /
Finanzas una cuenta de facturación** antes del taller: sin ella Cloud Run no
despliega. Es el bloqueador más común — el correo listo para copiar y las
alternativas sin tarjeta están en
[`cuenta-sin-tarjeta.md`](cuenta-sin-tarjeta.md).

```bash
gcloud config list
```
✅ Confirma la cuenta activa. Ten a mano el `.env` con tu API key funcionando.

> ⏱️ Recomendación fuerte: haz un ensayo completo (deploy + borrado) el día
> anterior. El primer despliegue de un proyecto nuevo tarda más porque Cloud
> Build construye la imagen desde cero.

---

## 2. El prompt principal (esto es lo que va en las slides)

Abre Claude Code **dentro de la carpeta del repo** y pega este prompt tal cual:

```text
Despliega este proyecto en Google Cloud Run usando la CLI de gcloud, paso a paso.

Contexto:
- Estoy en la carpeta del repo. Tiene un Dockerfile listo: FastAPI escuchando en $PORT (default 8080).
- Ya ejecuté `gcloud auth login` y tengo una cuenta de facturación activa.
- Mi API key de Anthropic está en el archivo .env local. NUNCA la imprimas en pantalla,
  ni la escribas en un archivo del repo, ni la pases como argumento visible: debe viajar
  solo por stdin hacia Secret Manager.

Ejecuta tú los comandos y verifica cada paso antes de seguir:

1. Crea un proyecto nuevo llamado workshop-agents-brayan y déjalo como proyecto activo.
   Vincúlale mi cuenta de facturación (si hay más de una, muéstrame las opciones y pregúntame).
2. Habilita las APIs necesarias: run, cloudbuild, artifactregistry y secretmanager.
3. Crea el secreto anthropic-api-key en Secret Manager tomando el valor desde mi .env,
   y dale el rol roles/secretmanager.secretAccessor a la service account que usa Cloud Run.
4. Despliega el servicio con:
   gcloud run deploy asistente-operaciones --source . --region southamerica-west1
   --allow-unauthenticated --set-secrets ANTHROPIC_API_KEY=anthropic-api-key:latest
   --set-env-vars MODEL=claude-sonnet-4-6
5. Verifica que quedó bien: haz un curl a /health (debe responder api_key_configured: true)
   y dime la Service URL final.
6. Muéstrame al final el comando exacto para borrar TODO cuando termine el taller.

Si un comando falla, diagnostica la causa y arréglalo antes de continuar.
Explica en una línea qué hace cada comando antes de ejecutarlo, para que la audiencia entienda.
```

Cambia `workshop-agents-brayan` por tu nombre: **el ID de proyecto debe ser
único a nivel mundial**.

---

## 3. Qué va a hacer Claude (para narrar en vivo)

Ten esto en las notas del orador — es el mapa de lo que la audiencia verá
pasar en pantalla:

| Paso | Comando que ejecuta Claude | Qué contar a la audiencia |
|---|---|---|
| 1 | `gcloud projects create` + `gcloud billing projects link` | "Un proyecto es la caja aislada donde vive todo; si la borras, no queda nada cobrando" |
| 2 | `gcloud services enable run... cloudbuild... secretmanager...` | "En la nube los servicios vienen apagados: pagas y activas solo lo que usas" |
| 3 | `gcloud secrets create` + `add-iam-policy-binding` | "La API key **nunca** entra al código ni a la imagen: va a una bóveda y el contenedor la recibe como variable de entorno al arrancar" |
| 4 | `gcloud run deploy --source .` | "Sin Docker local: Cloud Build lee el Dockerfile, construye la imagen en la nube y Cloud Run la ejecuta. Escala a cero cuando nadie la usa" |
| 5 | `curl .../health` | "El health check es cómo la nube sabe si tu contenedor está vivo" |

El momento que engancha: **abrir la Service URL en el teléfono** y mostrar que
el agente responde desde internet, no desde tu laptop.

---

## 4. Prompts de apoyo durante la demo

Para seguir jugando con Claude una vez que el servicio está arriba:

**Ver el agente trabajando en producción:**
```text
Muéstrame los logs del servicio en Cloud Run de los últimos 5 minutos y explícame
qué herramienta usó el agente en cada consulta.
```

**Personalizar y volver a desplegar (cierra el círculo con la Sesión 1):**
```text
Cambia el system prompt en app/config/system_prompt.txt para que el agente se llame
"Laura" y sea más formal, y vuelve a desplegar a Cloud Run. Avísame cuando la URL
esté sirviendo la versión nueva.
```

**Entender el costo (sin inventar cifras):**
```text
Explícame el modelo de cobro de Cloud Run para este servicio y muéstrame la página
oficial de pricing. No estimes montos: solo dime qué variables lo determinan.
```

**⚠️ Borrar todo al final (¡no olvidar!):**
```text
Borra todo lo que creamos hoy en GCP: el servicio de Cloud Run, el secreto y el
proyecto completo. Confirma al final que no queda nada que pueda generar costos.
```

---

## 5. Plan B si el deploy en vivo falla

Un despliegue en vivo puede fallar por red, cuota o facturación. Ten preparado:

1. **La guía manual**: [`01-cloud-run.md`](01-cloud-run.md), comando a comando —
   sirve para mostrar exactamente lo que Claude estaba haciendo.
2. **Un servicio ya desplegado el día anterior**: ten su URL a mano para
   mostrar el resultado final aunque el deploy en vivo se caiga.
3. **Captura de pantalla** de la Service URL funcionando en el teléfono.

### Fallos típicos y qué responder

| Error | Causa | Solución en vivo |
|---|---|---|
| `Reauthentication failed` | El token de gcloud expiró | `gcloud auth login` otra vez |
| `FAILED_PRECONDITION: Billing account ... not found` | Proyecto sin facturación vinculada | Vincúlala en la consola web: *Facturación → Vincular cuenta* |
| `PERMISSION_DENIED` al crear proyecto | Política de la organización lo bloquea | Usa un proyecto existente en vez de crear uno nuevo |
| `Revision ... failed` / el contenedor no arranca | El puerto no coincide | El Dockerfile ya usa `$PORT`; revisa que no se haya hardcodeado |
| `/chat` responde 503 en la nube | El secreto no llegó al contenedor | Revisa el binding IAM y el `--set-secrets` del paso 3 |

---

## 6. Después de la demo

Recuérdale a los participantes las dos ideas que se llevan:

1. **La arquitectura es la misma en las tres nubes** — mira la tabla de
   equivalencias del [README](../README.md#equivalencias-multi-cloud) y
   [`multi-cloud.md`](multi-cloud.md) para correr el agente con Claude en
   Bedrock o Vertex si el cliente lo exige.
2. **El secreto nunca vive en el código.** Si solo se llevan una práctica de
   la sesión, que sea esta.
