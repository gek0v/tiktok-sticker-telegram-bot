# Geko TikTok Sticker Telegram Bot (All-in-One Production)

Suite consolidada y lista para despliegue en la nube (**Render Free Tier $0**) del bot de stickers multimedia de TikTok para Telegram y WhatsApp.

---

## 🏗 Arquitectura del Contenedor All-in-One

El contenedor unifica los tres microservicios en una imagen Docker ligera (~280 MB RAM en pico):

1. **`signer-service` (`:8088`):** Microservicio criptográfico para la firma de peticiones móviles de ByteDance (X-Gorgon, X-Khronos, X-Argus, X-Ladon).
2. **`tiktok-sticker-service` (`:10000` / `$PORT`):** Backend FastAPI con cliente Aweme v37 y pipeline de transcodificación (WebP 512×512 y WebM VP9). Expone `/health` y `/api/v1/sticker/convert`.
3. **`geko-telegram-bot`:** Motor de Telegram Bot API con polling nativo y botones interactivos para descarga de stickers y documentos bajo demanda.

---

## 🚀 Despliegue en Render (Paso a Paso)

### Opción 1: Despliegue con Blueprint (`render.yaml`)
1. Sube este repositorio a tu cuenta de GitHub/GitLab.
2. Inicia sesión en [Render Dashboard](https://dashboard.render.com/).
3. Haz clic en **New +** > **Blueprint**.
4. Selecciona el repositorio. Render detectará automáticamente `render.yaml` y configurará el servicio.
5. Introduce el valor de `TELEGRAM_BOT_TOKEN` cuando te lo solicite y pulsa **Apply**.

### Opción 2: Despliegue Manual como Web Service
1. En [Render Dashboard](https://dashboard.render.com/), haz clic en **New +** > **Web Service**.
2. Conecta tu repositorio de GitHub/GitLab.
3. Configuración:
   - **Name:** `geko-tiktok-telegram-bot`
   - **Region:** Frankfurt (EU) u Ohio (US)
   - **Language / Runtime:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Instance Type:** `Free` ($0/mes)
4. En la sección **Environment Variables**, añade:
   - `TELEGRAM_BOT_TOKEN`: El token secreto de tu bot de Telegram obtenido de [@BotFather](https://t.me/BotFather).
   - `SIGNER_MODE`: `remote`
   - `REMOTE_SIGNER_URL`: `http://127.0.0.1:8088`
5. En **Health Check Path**, escribe: `/health`
6. Haz clic en **Create Web Service**.

---

## ⏰ Keep-Alive 24/7 (Evitar suspensión de 15 min en Render Free)

Los servicios gratuitos de Render entran en suspensión tras 15 minutos sin tráfico HTTP entrante. Para mantener el bot despierto y receptivo las 24 horas del día sin cold-starts:

1. Ve a un servicio gratuito de monitoreo como [Cron-job.org](https://cron-job.org) o [UptimeRobot](https://uptimerobot.com).
2. Crea un monitor **HTTP GET** con intervalo de **10 minutos**:
   - **URL:** `https://tu-servicio.onrender.com/health`
3. Esto enviará una petición periódica ligera que mantendrá el contenedor siempre activo al 100% sin agotar cuotas.
