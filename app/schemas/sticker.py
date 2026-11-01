from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, HttpUrl

class ResolveRequest(BaseModel):
    url: str = Field(..., description="TikTok share URL (e.g., https://vm.tiktok.com/ZN9yQoBn3UnNp-fnC62/)")

class ResolvedTarget(BaseModel):
    original_url: str
    expanded_url: str
    aweme_id: str
    comment_id: Optional[str] = None
    author_id: Optional[str] = None
    aweme_type: Optional[str] = None
    params: Dict[str, Any] = Field(default_factory=dict)

class MediaResource(BaseModel):
    sticker_id: Optional[str] = None
    display_name: Optional[str] = None
    content_type: int = Field(..., description="16/17 for catalog/IM stickers, 2/3 for user image attachments")
    is_animated: bool
    source_url: str
    fallback_urls: List[str] = Field(default_factory=list)
    width: Optional[int] = None
    height: Optional[int] = None

class ConvertRequest(BaseModel):
    url: Optional[str] = Field(None, description="TikTok share URL to resolve and convert directly")
    media_url: Optional[str] = Field(None, description="Direct URL of the media/sticker resource to convert directly")
    is_animated: Optional[bool] = None
    generate_tray: bool = Field(True, description="Whether to also generate a 96x96 tray icon (<50KB)")
    include_base64: bool = Field(True, description="Return base64 encoded sticker in JSON response")
    generate_telegram_webm: bool = Field(True, description="Whether to also generate Telegram VP9 WebM for animated stickers")

class TranscodeResult(BaseModel):
    success: bool
    is_animated: bool
    width: int = 512
    height: int = 512
    size_bytes: int
    size_kb: float
    frame_count: int
    duration_ms: Optional[int] = None
    fps: Optional[float] = None
    compliance: Dict[str, Any]
    base64_data: Optional[str] = None
    tray_icon_base64: Optional[str] = None
    tray_size_bytes: Optional[int] = None
    telegram_webm_base64: Optional[str] = None
    telegram_webm_size_bytes: Optional[int] = None
