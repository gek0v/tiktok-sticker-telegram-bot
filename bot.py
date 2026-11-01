"""
Geko Telegram Sticker Bot
Integrates with TikTok Mobile Aweme v37 Extractor and Transcoding Microservice.
Provides zero-friction sticker extraction and conversion over official Telegram Bot API.
Full support for Static WebP and Animated Video Stickers (VP9 WebM & WhatsApp WebP).
Interactive inline buttons for on-demand WebP/WebM document downloads.
"""

import asyncio
import base64
import io
import logging
import os
import re
import sys
import time
import uuid
import httpx
from PIL import Image

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.constants import ParseMode, ChatAction
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

# Logging configuration
logging.basicConfig(
    format="%(asctime)s - [%(levelname)s] - %(name)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger("GekoTelegramBot")

# Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://127.0.0.1:8000")
SIGNER_URL = os.environ.get("SIGNER_URL", "http://127.0.0.1:8088")
CACHE_BASE_DIR = "/tmp/bot_stickers"

os.makedirs(CACHE_BASE_DIR, exist_ok=True)

TIKTOK_REGEX = re.compile(r"https?://(?:[a-zA-Z0-9-]+\.)?tiktok\.com/[^\s]+", re.IGNORECASE)


def save_to_cache(files: dict) -> str:
    """Saves generated sticker assets to a temporary cache folder and returns its unique ID."""
    sid = uuid.uuid4().hex[:10]
    folder = os.path.join(CACHE_BASE_DIR, sid)
    os.makedirs(folder, exist_ok=True)
    for filename, content in files.items():
        if content:
            with open(os.path.join(folder, filename), "wb") as f:
                f.write(content)
    return sid


def create_sticker_from_image(img_bytes: bytes) -> bytes:
    """Normalizes any input image into Telegram/WhatsApp compliant 512x512 WebP."""
    im = Image.open(io.BytesIO(img_bytes))
    if im.mode != "RGBA":
        im = im.convert("RGBA")

    # Fit within 512x512 keeping aspect ratio
    im.thumbnail((512, 512), Image.Resampling.LANCZOS)

    # Center on 512x512 transparent canvas
    canvas = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    offset_x = (512 - im.width) // 2
    offset_y = (512 - im.height) // 2
    canvas.paste(im, (offset_x, offset_y), im)

    output = io.BytesIO()
    canvas.save(output, format="WEBP", quality=90, method=6)
    return output.getvalue()


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends welcome message and instructions."""
    text = (
        "🤖 *¡Bienvenido al Bot de Stickers de Geko!*\n\n"
        "Este bot está conectado a nuestro pipeline multimedia con motor **Aweme v37** y **Signer Móvil (X-Argus / X-Ladon / X-Gorgon)**.\n\n"
        "✨ *¿Qué puedes hacer?*\n"
        "1️⃣ *Extraer Stickers de TikTok:* Envíame cualquier enlace de TikTok con stickers en comentarios o imágenes.\n"
        "2️⃣ *Convertir Fotos a Stickers:* Envíame cualquier foto o imagen y la convertiré al instante en sticker 512x512.\n\n"
        "🎬 *Stickers Animados:* Detectamos automáticamente si el sticker es animado y te enviamos el sticker en movimiento con botones para descargar los archivos si los necesitas.\n\n"
        "🛠 *Comandos útiles:*\n"
        "• /status o /ping — Estado en tiempo real del backend y signer\n"
        "• /help — Instrucciones de uso"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends detailed help."""
    text = (
        "📖 *Guía de Uso - Geko Sticker Bot*\n\n"
        "*1. Extracción de TikTok:*\n"
        "Copia el enlace de un vídeo o comentario de TikTok y pégalo directamente en este chat:\n"
        "  • Si es un **sticker animado**: Recibirás el sticker nativo en movimiento (WebM VP9) con botones para descargar el archivo WebP (WhatsApp) o WebM (Telegram).\n"
        "  • Si es una **imagen o foto**: Se normaliza a sticker estático 512x512 centrado y transparente.\n\n"
        "*2. Creación Directa de Stickers:*\n"
        "Envía cualquier imagen como foto para generar tu sticker automáticamente."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Checks health of backend and signer services."""
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)

    start_t = time.time()
    backend_ok = False
    signer_ok = False
    backend_info = {}
    signer_info = {}

    async with httpx.AsyncClient(timeout=4.0) as client:
        try:
            r = await client.get(f"{BACKEND_URL}/health")
            if r.status_code == 200:
                backend_ok = True
                backend_info = r.json()
        except Exception as e:
            backend_info = {"error": str(e)}

        try:
            r2 = await client.get(f"{SIGNER_URL}/health")
            if r2.status_code == 200:
                signer_ok = True
                signer_info = r2.json()
        except Exception as e:
            signer_info = {"error": str(e)}

    elapsed_ms = int((time.time() - start_t) * 1000)
    status_icon = "🟢" if (backend_ok and signer_ok) else "🟡" if (backend_ok or signer_ok) else "🔴"

    text = (
        f"{status_icon} *Estado de los Servicios Geko*\n\n"
        f"• *Backend Multimedia:* {'Operativo ✅' if backend_ok else 'Desconectado ❌'}\n"
        f"   └ Versión: `{backend_info.get('version', 'N/A')}`\n"
        f"   └ Modo Signer: `{backend_info.get('signer_mode', 'N/A')}`\n"
        f"• *Signer Móvil (X-Argus/Gorgon):* {'Operativo ✅' if signer_ok else 'Desconectado ❌'}\n"
        f"   └ Servicio: `{signer_info.get('service', 'N/A')}`\n"
        f"• *Latencia Diagnóstico:* `{elapsed_ms} ms`\n\n"
        f"🔒 *Seguridad:* Oficial Telegram Bot API (0% riesgo personal, sin SIMs)."
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


async def handle_callback_query(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button clicks to download WebP or WebM files on demand."""
    query = update.callback_query
    await query.answer()

    data = query.data or ""
    if not data.startswith("dl:"):
        return

    parts = data.split(":")
    if len(parts) != 3:
        return

    _, sid, file_type = parts
    folder = os.path.join(CACHE_BASE_DIR, sid)

    if file_type == "webp":
        target_path = os.path.join(folder, "sticker_whatsapp.webp")
        filename = "sticker_whatsapp.webp"
        caption = "📁 *Archivo WebP descargado:* Optimizado para WhatsApp (512×512 transparente)."
        if not os.path.exists(target_path):
            target_path = os.path.join(folder, "sticker.webp")
            filename = "sticker.webp"
            caption = "📁 *Archivo WebP descargado:* Listo para usar o importar."
    elif file_type == "webm":
        target_path = os.path.join(folder, "sticker_telegram.webm")
        filename = "sticker_telegram.webm"
        caption = "📁 *Archivo WebM VP9 descargado:* Formato oficial para packs en Telegram (@Stickers)."
    else:
        return

    if not os.path.exists(target_path):
        await query.message.reply_text("⚠️ El archivo temporal ha expirado. Por favor, reenvía el enlace.")
        return

    try:
        with open(target_path, "rb") as f:
            file_bytes = f.read()

        doc_buf = io.BytesIO(file_bytes)
        doc_buf.name = filename
        await query.message.reply_document(
            document=doc_buf,
            filename=filename,
            caption=caption,
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        logger.error(f"Error sending cached document: {e}")
        await query.message.reply_text(f"❌ Error al enviar el archivo: {e}")


async def handle_message_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles text messages and extracts TikTok stickers if link is found."""
    text = update.message.text or ""
    chat_id = update.effective_chat.id

    match = TIKTOK_REGEX.search(text)
    if not match:
        await update.message.reply_text(
            "💡 Envíame un enlace de TikTok con stickers en comentarios o mándame una foto para convertirla a sticker."
        )
        return

    tiktok_url = match.group(0)
    logger.info(f"Processing TikTok URL: {tiktok_url}")

    status_msg = await update.message.reply_text("⏳ *Procesando sticker con Aweme v37 y transcoder...*", parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.CHOOSE_STICKER)

    try:
        api_url = f"{BACKEND_URL}/api/v1/sticker/convert"
        async with httpx.AsyncClient(timeout=35.0) as client:
            resp = await client.post(api_url, json={"url": tiktok_url, "include_base64": True})

        if resp.status_code != 200:
            error_detail = resp.text[:200]
            logger.warning(f"Backend failed for {tiktok_url}: HTTP {resp.status_code} - {error_detail}")
            await status_msg.edit_text(
                "⚠️ *No se pudo extraer el sticker de TikTok*\n"
                "Asegúrate de que el enlace apunta a un comentario con sticker o imagen válido.",
                parse_mode=ParseMode.MARKDOWN
            )
            return

        data = resp.json()
        is_animated = data.get("is_animated", False)
        size_kb = data.get("size_kb", 0.0)
        raw_webp = base64.b64decode(data["base64_data"]) if data.get("base64_data") else None
        raw_webm = base64.b64decode(data["telegram_webm_base64"]) if data.get("telegram_webm_base64") else None

        if is_animated and raw_webm:
            # Cache files for on-demand download button
            sid = save_to_cache({
                "sticker_whatsapp.webp": raw_webp,
                "sticker_telegram.webm": raw_webm,
            })

            keyboard = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("📥 Descargar WebP (WhatsApp)", callback_data=f"dl:{sid}:webp"),
                    InlineKeyboardButton("📁 Archivo WebM (Telegram)", callback_data=f"dl:{sid}:webm"),
                ]
            ])

            # Send single native animated Telegram Video Sticker (.webm) with download buttons
            try:
                webm_buf = io.BytesIO(raw_webm)
                webm_buf.name = "sticker.webm"
                await update.message.reply_sticker(sticker=webm_buf, reply_markup=keyboard)
            except Exception as e:
                logger.error(f"Failed to send native video sticker: {e}")
                if raw_webp:
                    await update.message.reply_document(
                        document=io.BytesIO(raw_webp),
                        filename="sticker_whatsapp.webp",
                        caption=f"🎬 Sticker animado ({size_kb:.1f} KB)"
                    )

        else:
            # Static Sticker
            if raw_webp:
                sid = save_to_cache({
                    "sticker.webp": raw_webp,
                })

                keyboard = InlineKeyboardMarkup([
                    [InlineKeyboardButton("📥 Descargar archivo WebP / WhatsApp", callback_data=f"dl:{sid}:webp")]
                ])

                webp_buf = io.BytesIO(raw_webp)
                webp_buf.name = "sticker.webp"
                try:
                    await update.message.reply_sticker(sticker=webp_buf, reply_markup=keyboard)
                except Exception as e:
                    logger.error(f"Failed to send native static sticker: {e}")
                    await update.message.reply_document(
                        document=io.BytesIO(raw_webp),
                        filename="sticker.webp",
                        caption=f"✅ Sticker estático ({size_kb:.1f} KB)"
                    )

        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as e:
        logger.exception("Error processing TikTok request")
        await status_msg.edit_text(
            f"❌ *Ocurrió un error al procesar el sticker:*\n`{str(e)}`",
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Converts user-sent photos directly into standard WebP stickers with download button."""
    chat_id = update.effective_chat.id
    status_msg = await update.message.reply_text("🎨 *Convirtiendo imagen a formato Sticker (512x512 WebP)...*", parse_mode=ParseMode.MARKDOWN)
    await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.CHOOSE_STICKER)

    try:
        photo_file = await update.message.photo[-1].get_file()
        photo_bytes = await photo_file.download_as_bytearray()

        webp_bytes = create_sticker_from_image(photo_bytes)
        size_kb = len(webp_bytes) / 1024.0

        sid = save_to_cache({
            "sticker.webp": webp_bytes,
        })

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("📥 Descargar archivo WebP / WhatsApp", callback_data=f"dl:{sid}:webp")]
        ])

        # Reply with single native sticker + inline download button
        await update.message.reply_sticker(sticker=io.BytesIO(webp_bytes), reply_markup=keyboard)

        try:
            await status_msg.delete()
        except Exception:
            pass

    except Exception as e:
        logger.exception("Error converting photo to sticker")
        await status_msg.edit_text(f"❌ *Error al convertir imagen:* `{str(e)}`", parse_mode=ParseMode.MARKDOWN)


def main():
    if not TELEGRAM_BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is missing!")
        sys.exit(1)

    logger.info("Initializing Geko Telegram Sticker Bot application...")
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("status", cmd_status))
    app.add_handler(CommandHandler("ping", cmd_status))

    # Callback Query for Download Buttons
    app.add_handler(CallbackQueryHandler(handle_callback_query))

    # Photo / Image
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

    # Text & TikTok URLs
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message_text))

    logger.info("Starting Telegram Bot long-polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
