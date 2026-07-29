# 💳 Desplegar sin poner tu tarjeta

La pregunta más común del taller: *"¿tengo que poner mi tarjeta para esto?"*

Respuesta honesta primero: **Google Cloud exige una cuenta de facturación para
usar Cloud Run, incluso si te vas a quedar dentro de la capa gratuita**, y
crear una cuenta de facturación requiere un medio de pago. Lo dice la
documentación oficial: *"durante el registro debes proporcionar una tarjeta de
crédito u otro método de pago válido"*
([Google Cloud Free Program](https://cloud.google.com/free/docs/free-cloud-features)).

> ⚠️ Si encuentras un blog o video que promete "GCP sin tarjeta con este
> truco", desconfía: o está desactualizado, o viola los términos de servicio,
> o te está vendiendo una cuenta de tercero. No lo uses, menos con datos de la
> empresa.

Lo que **sí** existe son tres rutas legítimas. La primera es la del taller.

| Ruta | ¿Tarjeta propia? | Cuándo usarla |
|---|---|---|
| **A. Facturación corporativa** | ❌ No | 👈 **La del taller.** Imagemaker paga, nadie expone su tarjeta |
| **B. Prueba gratis de GCP** | ✅ Sí (débito sirve) | Cuenta personal para practicar en casa |
| **C. Hugging Face Spaces** | ❌ No | Cero tarjeta, cero facturación: solo email |

---

## Ruta A — Usar la cuenta de facturación corporativa (recomendada)

Ningún participante pone tarjeta: se **reutiliza** la cuenta de facturación que
la empresa ya tiene. Tú (facilitador) haces esto una vez, antes del taller.

**1. Inicia sesión con tu cuenta corporativa:**

```bash
gcloud auth login
```
✅ Esperado: `You are now logged in as [brayan.villalobos@imagemaker.com]`.

**2. Revisa si ya tienes acceso a una cuenta de facturación:**

```bash
gcloud billing accounts list
```
✅ Esperado: al menos una fila con `OPEN: True`. Copia el `ACCOUNT_ID`
(formato `0X0X0X-0X0X0X-0X0X0X`).
❌ Si sale vacío: pasa al paso 3.

**3. Si salió vacío, pide acceso a TI / Finanzas.** Este es el correo que
puedes copiar y pegar:

> Asunto: Acceso a cuenta de facturación GCP para workshop interno
>
> Hola, estoy facilitando un workshop interno de agentes de IA y necesito
> desplegar una app de demo en Google Cloud Run.
>
> ¿Me pueden dar el rol **Usuario de cuenta de facturación**
> (`roles/billing.user`) sobre la cuenta de facturación de la organización,
> o indicarme el `billing account ID` a usar?
>
> Es una demo que se borra al terminar la sesión. El costo esperado es
> mínimo y queda dentro de la capa gratuita de Cloud Run; puedo dejar
> configurado un presupuesto con alertas y un tope.
>
> Gracias.

**4. Vincula la cuenta de facturación a tu proyecto del taller:**

```bash
gcloud billing projects link workshop-agents-brayan --billing-account=0X0X0X-0X0X0X-0X0X0X
```
✅ Esperado: `billingEnabled: true`.

**5. Blinda el gasto con un presupuesto y alertas** (2 minutos, en la consola
web — es más simple que por CLI):

1. Ve a <https://console.cloud.google.com/billing> → **Presupuestos y alertas**.
2. **Crear presupuesto** → alcance: solo tu proyecto `workshop-agents-...`.
3. Monto: algo simbólico (ej. USD 5) → alertas al 50%, 90% y 100%.
4. Guardar.

> 📌 Un presupuesto **avisa**, no corta el gasto automáticamente. La
> protección de verdad es borrar el proyecto al terminar (paso 6 de
> [`01-cloud-run.md`](01-cloud-run.md)).

---

## Ruta B — Prueba gratis de GCP (tarjeta propia, sin riesgo real)

Para practicar en casa con tu cuenta personal. **Requiere tarjeta**, pero el
miedo de fondo ("me van a cobrar sin avisar") no aplica. Lo que dice la
documentación oficial, verificado:

- Se hace una **autorización temporal de USD 0 a 1** para validar la tarjeta.
  Es una retención, **no un cobro**; se libera en días.
- Recibes **USD 300 de crédito para gastar en 90 días**.
- **No hay cobro automático al terminar.** La cuenta de prueba se cierra sola
  cuando gastas los 300 o pasan los 90 días, y hay **30 días de gracia** antes
  de que se borren los recursos. Para que te cobren, tienes que subir
  manualmente a cuenta de pago.
- Sirve **tarjeta de débito**, no solo crédito. Las **prepago suelen fallar**,
  igual que las tarjetas con pagos recurrentes bloqueados por el banco.

**Paso a paso:**

1. Entra a <https://cloud.google.com/free> → **Comenzar gratis**.
2. Inicia sesión con una cuenta de Google **personal** (no la corporativa, para
   no mezclar con la facturación de la empresa).
3. Paso 1 del formulario: país, tipo de cuenta **Individual**, acepta términos.
4. Paso 2: datos de la tarjeta (débito o crédito). Verás el aviso de que no se
   cobra automáticamente al final de la prueba.
5. **Comenzar mi prueba gratuita** → se crea el proyecto `My First Project` y
   una cuenta de facturación en modo prueba.
6. Verifica desde la terminal:

```bash
gcloud auth login
gcloud billing accounts list
```
✅ Esperado: una cuenta con `OPEN: True`.

**Truco para gastar cero:** despliega en una región con capa gratuita. El free
tier de Cloud Run aplica en las regiones de EE.UU. (`us-central1`, `us-east1`,
`us-west1`) y no en `southamerica-west1`. Consulta los límites y regiones
vigentes en <https://cloud.google.com/run/pricing> — cambian, no los memorices.

```bash
# Misma app, región con capa gratuita (más latencia desde Chile, costo cero)
gcloud run deploy asistente-operaciones --source . --region us-central1 \
  --allow-unauthenticated \
  --set-secrets "ANTHROPIC_API_KEY=anthropic-api-key:latest" \
  --set-env-vars "MODEL=claude-sonnet-4-6"
```

---

## Ruta C — Cero tarjeta, cero facturación: Hugging Face Spaces

Si no hay cuenta corporativa disponible y no quieres poner tarjeta, esta es la
salida real: **Hugging Face Spaces** ejecuta contenedores Docker gratis, solo
con una cuenta de email. Es el mismo `Dockerfile` del repo con dos ajustes.

**1. Crea la cuenta** en <https://huggingface.co/join> — email y contraseña,
sin medio de pago. Confirma el correo.

**2. Crea el Space:** <https://huggingface.co/new-space>

- **Space name**: `asistente-operaciones`
- **License**: la que prefieras (ej. `mit`)
- **SDK**: elige **Docker** → *Blank*
- **Hardware**: `CPU basic` (la opción gratuita)
- **Visibility**: 🔒 **Private** — importante, ver la advertencia de más abajo

**3. Guarda tu API key como secreto:** en el Space, **Settings** → **Variables
and secrets** → **New secret**:

- Name: `ANTHROPIC_API_KEY`
- Value: tu key

Los secretos llegan al contenedor como variables de entorno en tiempo de
ejecución, que es exactamente lo que `app/main.py` ya lee. **No** hay que tocar
el código.

**4. Ajusta el `Dockerfile` para Spaces.** Hugging Face ejecuta el contenedor
con el usuario `1000` y enruta el tráfico al puerto declarado en `app_port`
(7860 por defecto). Crea el archivo `Dockerfile` del Space así:

```dockerfile
FROM python:3.12-slim

# Spaces corre el contenedor como usuario 1000: creamos ese usuario y
# trabajamos en su carpeta para no chocar con los permisos.
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# requirements primero: aprovecha el cache de capas de Docker
COPY --chown=user requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=user app/ ./app/

# 7860 es el puerto que Spaces expone por defecto
ENV PORT=7860
CMD uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**5. Verifica el `README.md` del Space.** Hugging Face lo crea solo; confirma
que el bloque de arriba (frontmatter) tenga el puerto correcto:

```yaml
---
title: Asistente de Operaciones
emoji: 🤖
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
---
```

**6. Sube los archivos.** Por la web (**Files** → **Add file** → *Upload
files*): el `Dockerfile`, `requirements.txt` y toda la carpeta `app/`. O por
git, si te acomoda más:

```bash
git clone https://huggingface.co/spaces/TU-USUARIO/asistente-operaciones
```

**7. Espera el build** (~3-5 min; la pestaña **Logs** muestra el avance) y abre
la URL del Space.
✅ Esperado: la misma UI de chat, ahora servida desde internet.

### ⚠️ Advertencia que aplica a las tres rutas

Un despliegue **público** (un Space público, o Cloud Run con
`--allow-unauthenticated`) significa que **cualquiera con el link puede
conversar con tu agente, y cada mensaje consume tu API key**. Para una demo de
taller está bien porque dura una hora, pero:

- Deja el Space en **Private** mientras pruebas.
- **Borra el despliegue al terminar** el taller.
- Si el link se compartió, **rota la API key** en
  <https://platform.claude.com/> (revocar y crear una nueva).

---

## ¿Cuál elijo para el taller?

- **Facilitador**: Ruta A. Consíguete la cuenta de facturación corporativa con
  días de anticipación — es el bloqueador clásico de estas sesiones.
- **Participantes que quieran seguir practicando**: Ruta B en casa (débito
  sirve, y en `us-central1` el costo es cero), o Ruta C si no quieren dar
  ninguna tarjeta.
- **Si el día del taller no hay facturación**: haz el deploy en Hugging Face
  (Ruta C) y muestra la guía de Cloud Run
  ([`01-cloud-run.md`](01-cloud-run.md)) explicando cómo sería en la nube del
  cliente. El concepto que se enseña —contenedor + secreto + URL pública— es
  idéntico.
