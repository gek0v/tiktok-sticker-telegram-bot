try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.config import settings
from app.api.routes import router as sticker_router

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Microservice for extracting TikTok stickers (Aweme API, Gorgon/Khronos signatures) and transcoding to WhatsApp WebP specification."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sticker_router)

@app.get("/", tags=["System"])
async def root():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }

@app.get("/health", tags=["System"])
async def health_check():
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "signer_mode": settings.SIGNER_MODE,
        "limits": {
            "whatsapp_animated_max_kb": settings.WA_MAX_ANIMATED_SIZE_BYTES / 1024,
            "whatsapp_static_max_kb": settings.WA_MAX_STATIC_SIZE_BYTES / 1024,
            "whatsapp_canvas": f"{settings.WA_CANVAS_SIZE}x{settings.WA_CANVAS_SIZE}",
            "whatsapp_duration_max_sec": settings.WA_MAX_DURATION_MS / 1000
        }
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"detail": f"Internal Server Error: {str(exc)}"}
    )
