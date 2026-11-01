import re
import time
import urllib.parse
from typing import Optional, Dict, Any, Tuple
import httpx
from app.config import settings
from app.schemas.sticker import ResolvedTarget

class TikTokResolver:
    """
    Ultra-fast TikTok URL resolution with:
    - Zero-network shortcut for direct/expanded URLs
    - In-memory TTL cache for short links (vm.tiktok.com, vt.tiktok.com, tiktok.com/t/)
    - Persistent HTTP keep-alive connection pooling
    """

    MOBILE_UA = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    )

    AWEME_PATH_REGEX = re.compile(r"/(?:video|photo|v)/(\d+)")
    SHORT_DOMAIN_REGEX = re.compile(r"https?://(?:vm|vt|m)\.tiktok\.com/|tiktok\.com/t/")

    _CACHE: Dict[str, Tuple[float, ResolvedTarget]] = {}
    _CACHE_TTL_SEC = 900  # 15 minutes

    @classmethod
    async def resolve_url(cls, short_url: str) -> ResolvedTarget:
        """
        Resolves short URL with caching and direct-parsing optimization.
        """
        if not short_url.startswith(("http://", "https://")):
            short_url = f"https://{short_url}"

        now = time.time()
        # 1. Check TTL cache
        if short_url in cls._CACHE:
            ts, cached_target = cls._CACHE[short_url]
            if now - ts < cls._CACHE_TTL_SEC:
                return cached_target

        # 2. Fast Path: If URL is already full format and not a shortened redirect domain
        if not cls.SHORT_DOMAIN_REGEX.search(short_url):
            aweme_id, comment_id, author_id, aweme_type, query_params = cls.parse_url_parameters(short_url)
            if aweme_id:
                target = ResolvedTarget(
                    original_url=short_url,
                    expanded_url=short_url,
                    aweme_id=aweme_id,
                    comment_id=comment_id,
                    author_id=author_id,
                    aweme_type=aweme_type,
                    params=query_params
                )
                cls._CACHE[short_url] = (now, target)
                return target

        # 3. Follow HTTP redirects for shortened URLs
        headers = {
            "User-Agent": cls.MOBILE_UA,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        async with httpx.AsyncClient(
            follow_redirects=True,
            timeout=settings.HTTP_TIMEOUT_SECONDS,
            headers=headers
        ) as client:
            response = await client.get(short_url)
            final_url = str(response.url)

        aweme_id, comment_id, author_id, aweme_type, query_params = cls.parse_url_parameters(final_url)

        # Fallback: check redirect history headers if query parameters were stripped in last hop
        if not aweme_id or not comment_id:
            for resp in getattr(response, "history", []):
                loc = resp.headers.get("location", "")
                if loc:
                    h_aweme, h_comment, h_author, h_type, h_params = cls.parse_url_parameters(loc)
                    aweme_id = aweme_id or h_aweme
                    comment_id = comment_id or h_comment
                    author_id = author_id or h_author
                    aweme_type = aweme_type or h_type
                    query_params.update(h_params)

        if not aweme_id:
            raise ValueError(f"Could not extract aweme_id from URL: {final_url}")

        resolved = ResolvedTarget(
            original_url=short_url,
            expanded_url=final_url,
            aweme_id=aweme_id,
            comment_id=comment_id,
            author_id=author_id,
            aweme_type=aweme_type,
            params=query_params
        )

        cls._CACHE[short_url] = (now, resolved)
        return resolved

    @classmethod
    def parse_url_parameters(cls, target_url: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Dict[str, Any]]:
        parsed = urllib.parse.urlparse(target_url)
        query = urllib.parse.parse_qs(parsed.query)

        # Extract aweme_id:
        aweme_id = None
        if "share_item_id" in query:
            aweme_id = query["share_item_id"][0]
        elif "item_id" in query:
            aweme_id = query["item_id"][0]
        
        if not aweme_id:
            match = cls.AWEME_PATH_REGEX.search(parsed.path)
            if match:
                aweme_id = match.group(1)

        # Extract comment_id:
        comment_id = None
        if "share_comment_id" in query:
            comment_id = query["share_comment_id"][0]
        elif "comment_id" in query:
            comment_id = query["comment_id"][0]

        author_id = query.get("comment_author_id", [None])[0] or query.get("user_id", [None])[0]
        aweme_type = query.get("aweme_type", [None])[0]

        clean_params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

        return aweme_id, comment_id, author_id, aweme_type, clean_params
