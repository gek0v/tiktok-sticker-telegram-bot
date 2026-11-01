import re
import urllib.parse
from typing import Optional, Dict, Any, Tuple
import httpx
from app.config import settings
from app.schemas.sticker import ResolvedTarget

class TikTokResolver:
    """
    Handles TikTok short URL resolution (vm.tiktok.com, vt.tiktok.com, etc.),
    tracking HTTP redirects and parsing canonical Aweme item and comment IDs.
    """

    MOBILE_UA = (
        "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
    )

    AWEME_PATH_REGEX = re.compile(r"/(?:video|photo|v)/(\d+)")

    @classmethod
    async def resolve_url(cls, short_url: str) -> ResolvedTarget:
        """
        Follows HTTP redirects using a mobile user-agent to preserve TikTok share query parameters.
        Extracts aweme_id, comment_id, and metadata.
        """
        if not short_url.startswith(("http://", "https://")):
            short_url = f"https://{short_url}"

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

        return ResolvedTarget(
            original_url=short_url,
            expanded_url=final_url,
            aweme_id=aweme_id,
            comment_id=comment_id,
            author_id=author_id,
            aweme_type=aweme_type,
            params=query_params
        )

    @classmethod
    def parse_url_parameters(cls, target_url: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str], Dict[str, Any]]:
        parsed = urllib.parse.urlparse(target_url)
        query = urllib.parse.parse_qs(parsed.query)

        # Extract aweme_id:
        # Priority 1: share_item_id or item_id in query params
        aweme_id = None
        if "share_item_id" in query:
            aweme_id = query["share_item_id"][0]
        elif "item_id" in query:
            aweme_id = query["item_id"][0]
        
        # Priority 2: regex match on URL path (/video/123... or /photo/123...)
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

        # Extract author_id & aweme_type
        author_id = query.get("comment_author_id", [None])[0] or query.get("user_id", [None])[0]
        aweme_type = query.get("aweme_type", [None])[0]

        clean_params = {k: v[0] if len(v) == 1 else v for k, v in query.items()}

        return aweme_id, comment_id, author_id, aweme_type, clean_params
