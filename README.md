# Geko TikTok Sticker Telegram Bot (All-in-One Production)

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/gek0v/tiktok-sticker-telegram-bot)

Suite consolidada y lista para despliegue en la nube (**Render Free Tier $0**) del bot de stickers multimedia de TikTok para Telegram y WhatsApp.

---

## 🏗 Arquitectura del Contenedor All-in-One

El contenedor unifica los tres microservicios en una imagen Docker ligera (~280 MB RAM en pico):

1. **`signer-service` (`:8088`):** Microservicio criptográfico para la firma de peticiones móviles de ByteDance (X-Gorgon, X-Khronos, X-Argus, X-Ladon).
2. **`tiktok-sticker-service` (`:10000` / `$PORT`):** Backend FastAPI con cliente Aweme v37 y pipeline de transcodificación (WebP 512×512 y WebM VP9). Expone `/health` y `/api/v1/sticker/convert`.
3. **`geko-telegram-bot`:** Motor de Telegram Bot API con polling nativo y botones interactivos para descarga de stickers y documentos bajo demanda.

---

## 🚀 Despliegue en Render (1 Clic)

### Opción 1: Despliegue Automático con Botón Directo
Haz clic en el siguiente enlace para desplegar directamente con la configuración predefinida:

👉 **[Desplegar en Render (1-Click Deploy)](https://render.com/deploy?repo=https://github.com/gek0v/tiktok-sticker-telegram-bot)**

Render leerá automáticamente el archivo `render.yaml`, preparará el contenedor Docker y solo te solicitará rellenar el token de Telegram:
* **`TELEGRAM_BOT_TOKEN`**: Tu token de Telegram de [@BotFather](https://t.me/BotFather).

### Opción 2: Despliegue Manual como Web Service
1. En [Render Dashboard](https://dashboard.render.com/), haz clic en **New +** > **Web Service**.
2. Conecta tu repositorio: `https://github.com/gek0v/tiktok-sticker-telegram-bot`.
3. Configuración:
   - **Name:** `geko-tiktok-telegram-bot`
   - **Region:** Frankfurt (EU) u Ohio (US)
   - **Language / Runtime:** `Docker`
   - **Dockerfile Path:** `./Dockerfile`
   - **Instance Type:** `Free` ($0/mes)
4. En **Environment Variables**, añade:
   - `TELEGRAM_BOT_TOKEN`: El token secreto de tu bot de Telegram.
   - `SIGNER_MODE`: `remote`
   - `REMOTE_SIGNER_URL`: `http://127.0.0.1:8088`
5. En **Health Check Path**, escribe: `/health`
6. Haz clic en **Create Web Service**.

---

## ⏰ Keep-Alive 24/7 (Evitar suspensión de 15 min en Render Free)

Los servicios gratuitos de Render entran en suspensión tras 15 minutos sin tráfico HTTP entrante. Para mantener el bot despierto y receptivo las 24 horas del día sin cold-starts:

1. Ve a un servicio gratuito de monitoreo como [Cron-job.org](https://cron-job.org) o [UptimeRobot](https://uptimerobot.com).
2. Crea un monitor **HTTP GET** con intervalo de **10 minutos**:
   - **URL:** `https://tu-servicio.onrender.com/health` (sustituye por la URL que te asigne Render al desplegar).
3. Esto enviará una petición periódica ultra ligera que mantendrá el contenedor siempre activo al 100% sin agotar cuotas.
