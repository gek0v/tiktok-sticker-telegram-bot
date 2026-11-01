import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra="ignore")

    # Service Info
    APP_NAME: str = "tiktok-whatsapp-sticker-service"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Aweme Mobile API Endpoints
    AWEME_BASE_URL: str = "https://api16-normal-c-useast1a.tiktokv.com"
    AWEME_COMMENT_PATH: str = "/aweme/v2/comment/list/"
    
    # Device Simulation Defaults (Aligned with TikTok v37.0.4 for cmt_sticker_struct support)
    DEFAULT_AID: int = 1233
    DEFAULT_APP_NAME: str = "musical_ly"
    DEFAULT_VERSION_CODE: str = "370004"
    DEFAULT_VERSION_NAME: str = "37.0.4"
    DEFAULT_DEVICE_TYPE: str = "Pixel 7"
    DEFAULT_DEVICE_BRAND: str = "Google"
    DEFAULT_OS_VERSION: str = "13"
    DEFAULT_OS_API: str = "33"
    DEFAULT_CHANNEL: str = "googleplay"

    # Signature Strategy: "local" (built-in v04 generator) or "remote" (Unidbg/Sekiro/TikTokSigner microservice)
    SIGNER_MODE: str = "remote"
    REMOTE_SIGNER_URL: str = Field(default="http://127.0.0.1:8088", description="URL of remote Gorgon/Argus signer service if SIGNER_MODE='remote'")
    SIGNER_TIMEOUT_SEC: float = 5.0

    # WhatsApp Sticker Strict Specifications
    WA_CANVAS_SIZE: int = 512
    WA_SAFE_PADDING: int = 16  # Active content fits in (512 - 2*16) = 480x480
    WA_MAX_ANIMATED_SIZE_BYTES: int = 490 * 1024  # WhatsApp hard limit is 500 KB (< 500 KB strictly)
    WA_MAX_STATIC_SIZE_BYTES: int = 100 * 1024    # WhatsApp static sticker limit is 100 KB
    WA_MAX_DURATION_MS: int = 3000                 # WhatsApp limit: <= 3.0 seconds
    WA_TARGET_FPS_MIN: int = 15
    WA_TARGET_FPS_MAX: int = 20
    WA_TRAY_ICON_SIZE: int = 96
    WA_MAX_TRAY_SIZE_BYTES: int = 50 * 1024        # WhatsApp tray icon limit: < 50 KB

    # HTTP Client timeouts
    HTTP_TIMEOUT_SECONDS: float = 15.0

settings = Settings()
