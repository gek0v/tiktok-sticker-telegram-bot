import urllib.parse
from typing import Optional, List, Dict, Any
import httpx
from app.config import settings
from app.services.signer import BaseSigner, get_signer
from app.schemas.sticker import MediaResource

class AwemeClient:
    """
    Client for ByteDance Aweme API with device simulation and signature headers.
    Specialized in extracting comment media items (catalog stickers content_type 16/17,
    and user image attachments content_type 2/3).
    """

    APP_USER_AGENT = (
        f"com.zhiliaoapp.musically/{settings.DEFAULT_VERSION_CODE} (Linux; U; Android {settings.DEFAULT_OS_VERSION}; "
        f"en_US; {settings.DEFAULT_DEVICE_TYPE}; Build/TQ3A.230901.001; Cronet/TTNetVersion:61633535)"
    )

    def __init__(self, signer: Optional[BaseSigner] = None):
        self.signer = signer or get_signer()

    def build_device_params(self, aweme_id: str, comment_id: Optional[str] = None) -> Dict[str, str]:
        params = {
            "aweme_id": str(aweme_id),
            "cursor": "0",
            "count": "20",
            "aid": str(settings.DEFAULT_AID),
            "app_name": settings.DEFAULT_APP_NAME,
            "version_code": settings.DEFAULT_VERSION_CODE,
            "version_name": settings.DEFAULT_VERSION_NAME,
            "device_type": settings.DEFAULT_DEVICE_TYPE,
            "device_brand": settings.DEFAULT_DEVICE_BRAND,
            "os_version": settings.DEFAULT_OS_VERSION,
            "os_api": settings.DEFAULT_OS_API,
            "channel": settings.DEFAULT_CHANNEL,
            "device_id": "7290184719283746192",
            "openudid": "9a8b7c6d5e4f3a2b",
            "iid": "7290184719283746192",
            "resolution": "1080*2400",
            "dpi": "420",
            "language": "en",
        }
        if comment_id:
            # TikTok Aweme uses insert_ids to force-pin the target comment in the response
            params["insert_ids"] = str(comment_id)

        return params

    async def fetch_comment_media(self, aweme_id: str, comment_id: Optional[str] = None) -> MediaResource:
        """
        Executes signed request against /aweme/v2/comment/list/ and extracts the media resource.
        """
        params = self.build_device_params(aweme_id, comment_id)
        query_string = urllib.parse.urlencode(params)
        full_url = f"{settings.AWEME_BASE_URL}{settings.AWEME_COMMENT_PATH}?{query_string}"

        # 1. Sign request with Gorgon, Khronos, Argus & Ladon
        security_headers = await self.signer.sign_request(url_query=query_string)

        headers = {
            "User-Agent": self.APP_USER_AGENT,
            "Accept": "application/json",
            "Accept-Encoding": "gzip",
            **security_headers
        }

        # 2. Make request
        try:
            async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
                resp = await client.get(full_url, headers=headers)
                if resp.status_code == 200 and resp.content:
                    data = resp.json()
                    media = self.parse_comment_payload(data, comment_id)
                    if media:
                        return media
        except Exception:
            # If network error or mobile endpoint blocked, try web comment API fallback
            pass

        # 3. Fallback: Query Web / Mobile Comment API with device simulation
        fallback_media = await self.fetch_web_comment_fallback(aweme_id, comment_id)
        if fallback_media:
            return fallback_media

        raise ValueError(f"Could not locate media resource for comment {comment_id} on aweme {aweme_id}")

    def parse_comment_payload(self, data: Dict[str, Any], target_comment_id: Optional[str]) -> Optional[MediaResource]:
        comments = data.get("comments") or []
        if not comments:
            return None

        # Search for requested comment strictly: do NOT fallback to comments[0] if target_comment_id was given
        target_comment = None
        if target_comment_id:
            for c in comments:
                if str(c.get("cid")) == str(target_comment_id):
                    target_comment = c
                    break
            if not target_comment:
                return None
        elif comments:
            target_comment = comments[0]
        else:
            return None

        # Determine media type:
        # Case A: cmt_sticker_struct (TikTok v37+ animated & static catalog stickers / video2stickers)
        cmt_sticker = target_comment.get("cmt_sticker_struct")
        if cmt_sticker:
            return self._extract_from_cmt_sticker_struct(cmt_sticker, content_type=target_comment.get("content_type", 17))

        # Case B: content_type 16/17 (Legacy catalog sticker / IM Emoji)
        sticker_obj = target_comment.get("sticker")
        if sticker_obj:
            return self._extract_from_sticker_object(sticker_obj, content_type=target_comment.get("content_type", 17))

        # Case C: content_type 2/3 (User uploaded image list)
        image_list = target_comment.get("image_list")
        if image_list and len(image_list) > 0:
            return self._extract_from_image_list(image_list[0], content_type=3)

        return None

    def _extract_from_cmt_sticker_struct(self, cmt_sticker: Dict[str, Any], content_type: int = 17) -> MediaResource:
        animated_obj = cmt_sticker.get("animated_url") or {}
        static_obj = cmt_sticker.get("static_url") or {}

        anim_urls = []
        for res_key in ("high_resolution_url", "mid_resolution_url", "low_resolution_url"):
            res = animated_obj.get(res_key)
            if res and isinstance(res, dict) and res.get("url_list"):
                anim_urls.extend(res["url_list"])

        static_urls = []
        for res_key in ("high_resolution_url", "mid_resolution_url", "low_resolution_url"):
            res = static_obj.get(res_key)
            if res and isinstance(res, dict) and res.get("url_list"):
                static_urls.extend(res["url_list"])

        urls = anim_urls or static_urls
        if not urls:
            raise ValueError("cmt_sticker_struct has no valid URL list")

        is_animated = bool(anim_urls)
        res_info = animated_obj.get("high_resolution_url") or static_obj.get("high_resolution_url") or {}
        w = res_info.get("width", 512) if isinstance(res_info, dict) else 512
        h = res_info.get("height", 512) if isinstance(res_info, dict) else 512

        return MediaResource(
            sticker_id=str(cmt_sticker.get("id", "")),
            display_name=cmt_sticker.get("name") or "TikTok Sticker",
            content_type=content_type,
            is_animated=is_animated,
            source_url=urls[0],
            fallback_urls=urls[1:] if len(urls) > 1 else [],
            width=w,
            height=h
        )

    def _extract_from_sticker_object(self, sticker: Dict[str, Any], content_type: int = 17) -> MediaResource:
        animate_urls = (
            sticker.get("animate_url", {}).get("url_list") or 
            sticker.get("url", {}).get("url_list") or 
            []
        )
        static_urls = (
            sticker.get("static_url", {}).get("url_list") or 
            sticker.get("url", {}).get("url_list") or 
            []
        )

        urls = animate_urls or static_urls
        if not urls:
            raise ValueError("Sticker object has no valid URL list")

        is_animated = bool(animate_urls) or any(".webp" in u or "anim" in u for u in urls)

        return MediaResource(
            sticker_id=str(sticker.get("id", "")),
            display_name=sticker.get("display_name"),
            content_type=content_type,
            is_animated=is_animated,
            source_url=urls[0],
            fallback_urls=urls[1:] if len(urls) > 1 else [],
            width=sticker.get("width"),
            height=sticker.get("height")
        )

    def _extract_from_image_list(self, img_item: Dict[str, Any], content_type: int = 3) -> MediaResource:
        urls = (
            img_item.get("origin_url", {}).get("url_list") or 
            img_item.get("download_url", {}).get("url_list") or 
            []
        )
        if not urls:
            raise ValueError("Image list item has no valid URL list")

        return MediaResource(
            content_type=content_type,
            is_animated=False,
            source_url=urls[0],
            fallback_urls=urls[1:] if len(urls) > 1 else [],
            width=img_item.get("width"),
            height=img_item.get("height")
        )

    async def fetch_web_comment_fallback(self, aweme_id: str, comment_id: Optional[str] = None) -> Optional[MediaResource]:
        """
        Public comment endpoint fallback with device simulation and pagination
        when mobile endpoint requires captcha/device refresh.
        """
        web_url = "https://www.tiktok.com/api/comment/list/"
        headers = {
            "User-Agent": self.APP_USER_AGENT,
            "Referer": "https://www.tiktok.com/"
        }
        
        cursor = 0
        max_pages = 6

        async with httpx.AsyncClient(timeout=settings.HTTP_TIMEOUT_SECONDS) as client:
            for page in range(max_pages):
                params = {
                    "aweme_id": str(aweme_id),
                    "count": "50",
                    "cursor": str(cursor),
                    "aid": str(settings.DEFAULT_AID),
                    "device_type": settings.DEFAULT_DEVICE_TYPE,
                    "app_type": "normal",
                    "app_name": settings.DEFAULT_APP_NAME,
                    "channel": settings.DEFAULT_CHANNEL,
                    "device_platform": "android",
                    "version_code": settings.DEFAULT_VERSION_CODE,
                    "version_name": settings.DEFAULT_VERSION_NAME,
                }
                if comment_id:
                    params["insert_ids"] = str(comment_id)

                try:
                    res = await client.get(web_url, params=params, headers=headers)
                    if res.status_code == 200:
                        data = res.json()
                        media = self.parse_comment_payload(data, comment_id)
                        if media:
                            return media
                        
                        has_more = data.get("has_more")
                        next_cursor = data.get("cursor")
                        if not has_more or next_cursor == cursor or not data.get("comments"):
                            break
                        cursor = next_cursor
                    else:
                        break
                except Exception:
                    break

        return None
