from fastapi import APIRouter, Depends, HTTPException, Query, Response
import httpx
from app.config import settings
from app.schemas.sticker import (
    ResolveRequest, 
    ResolvedTarget, 
    MediaResource, 
    ConvertRequest, 
    TranscodeResult
)
from app.api.dependencies import get_resolver, get_aweme_client, get_transcoder
from app.services.resolver import TikTokResolver
from app.services.aweme_client import AwemeClient
from app.services.transcoder import StickerTranscoder

router = APIRouter(prefix="/api/v1/sticker", tags=["Stickers"])

@router.post("/resolve", response_model=dict)
async def resolve_tiktok_sticker(
    request: ResolveRequest,
    resolver: TikTokResolver = Depends(get_resolver),
    aweme_client: AwemeClient = Depends(get_aweme_client)
):
    """
    Step 1: Resolves TikTok shortened URL and extracts aweme_id & comment_id.
    Step 2: Fetches Aweme comment list using device parameters & Gorgon signature.
    Returns parsed metadata and original CDN media resource.
    """
    try:
        resolved = await resolver.resolve_url(request.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to resolve TikTok URL: {str(e)}")

    try:
        media = await aweme_client.fetch_comment_media(
            aweme_id=resolved.aweme_id,
            comment_id=resolved.comment_id
        )
    except Exception as e:
        # Return resolution even if media fetch fails or needs authentication
        return {
            "target": resolved,
            "media": None,
            "error": str(e)
        }

    return {
        "target": resolved,
        "media": media
    }

@router.post("/convert", response_model=TranscodeResult)
async def convert_tiktok_sticker(
    request: ConvertRequest,
    resolver: TikTokResolver = Depends(get_resolver),
    aweme_client: AwemeClient = Depends(get_aweme_client),
    transcoder: StickerTranscoder = Depends(get_transcoder)
):
    """
    End-to-End: Resolves URL, extracts media from Aweme, and transcodes strictly
    to WhatsApp WebP specifications (512x512, <500KB animated, <=3s, loop 0).
    """
    target_media_url = request.media_url
    is_animated_hint = request.is_animated

    # 1. If TikTok share URL is provided, resolve & locate media resource
    if not target_media_url and request.url:
        resolved = await resolver.resolve_url(request.url)
        media = await aweme_client.fetch_comment_media(
            aweme_id=resolved.aweme_id,
            comment_id=resolved.comment_id
        )
        target_media_url = media.source_url
        is_animated_hint = media.is_animated

    if not target_media_url:
        raise HTTPException(status_code=400, detail="Either 'url' or 'media_url' must be provided")

    # 2. Download original CDN media bytes
    try:
        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            resp = await client.get(target_media_url, headers={
                "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X)"
            })
            if resp.status_code != 200:
                raise HTTPException(status_code=502, detail=f"Failed downloading CDN resource: HTTP {resp.status_code}")
            raw_bytes = resp.content
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error downloading media: {str(e)}")

    # 3. Transcode to WhatsApp WebP
    try:
        sticker_bytes, tray_bytes, result = transcoder.transcode(
            raw_bytes=raw_bytes,
            is_animated_hint=is_animated_hint,
            generate_tray=request.generate_tray
        )
        if not request.include_base64:
            result.base64_data = None
            result.tray_icon_base64 = None
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcoding pipeline failed: {str(e)}")

@router.get("/direct-webp")
async def get_direct_webp(
    url: str = Query(..., description="TikTok share URL or direct media URL"),
    resolver: TikTokResolver = Depends(get_resolver),
    aweme_client: AwemeClient = Depends(get_aweme_client),
    transcoder: StickerTranscoder = Depends(get_transcoder)
):
    """
    Returns the binary image/webp stream directly for immediate WhatsApp import or preview.
    """
    target_media_url = url
    is_animated_hint = None

    if "tiktok.com" in url:
        resolved = await resolver.resolve_url(url)
        media = await aweme_client.fetch_comment_media(
            aweme_id=resolved.aweme_id,
            comment_id=resolved.comment_id
        )
        target_media_url = media.source_url
        is_animated_hint = media.is_animated

    async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
        resp = await client.get(target_media_url)
        raw_bytes = resp.content

    sticker_bytes, _, _ = transcoder.transcode(raw_bytes, is_animated_hint=is_animated_hint)

    return Response(
        content=sticker_bytes,
        media_type="image/webp",
        headers={"Content-Disposition": "inline; filename=\"sticker.webp\""}
    )
