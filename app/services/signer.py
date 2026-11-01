import time
import hashlib
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import httpx
from app.config import settings

class BaseSigner(ABC):
    @abstractmethod
    async def sign_request(self, url_query: str, body: Optional[bytes] = None, cookies: Optional[str] = None) -> Dict[str, str]:
        """
        Generates security headers for Aweme mobile API request.
        Returns dict containing X-Gorgon, X-Khronos, X-SS-REQ-TICKET, X-Argus, X-Ladon, etc.
        """
        pass

class LocalGorgonSigner(BaseSigner):
    """
    Local implementation of ByteDance Gorgon v04 signature algorithm.
    Derives X-Gorgon from URL query string, request body MD5, cookie MD5, and Khronos timestamp.
    """

    @staticmethod
    def _md5(data: str or bytes) -> str:
        if isinstance(data, str):
            data = data.encode("utf-8")
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def _hex_to_bytes(hex_str: str) -> list:
        return [int(hex_str[i:i+2], 16) for i in range(0, len(hex_str), 2)]

    @classmethod
    def generate_gorgon(cls, khronos: int, url_query: str, body: Optional[bytes] = None, cookie: Optional[str] = None) -> str:
        url_md5 = cls._md5(url_query) if url_query else "0" * 32
        body_md5 = cls._md5(body) if body else "0" * 32
        cookie_md5 = cls._md5(cookie) if cookie else "0" * 32

        url_bytes = cls._hex_to_bytes(url_md5)
        body_bytes = cls._hex_to_bytes(body_md5)
        cookie_bytes = cls._hex_to_bytes(cookie_md5)

        payload = [0] * 20
        payload[0] = url_bytes[14]
        payload[1] = url_bytes[15]
        payload[2] = url_bytes[13]
        payload[3] = url_bytes[12]

        payload[4] = body_bytes[14]
        payload[5] = body_bytes[15]
        payload[6] = body_bytes[13]
        payload[7] = body_bytes[12]

        payload[8] = cookie_bytes[14]
        payload[9] = cookie_bytes[15]
        payload[10] = cookie_bytes[13]
        payload[11] = cookie_bytes[12]

        payload[12] = 0
        payload[13] = 0
        payload[14] = 0
        payload[15] = 0

        payload[16] = (khronos >> 24) & 0xFF
        payload[17] = (khronos >> 16) & 0xFF
        payload[18] = (khronos >> 8) & 0xFF
        payload[19] = khronos & 0xFF

        trans_table = [
            0xDF, 0x77, 0xB9, 0x40, 0x6C, 0x20, 0x9B, 0xE2, 
            0x83, 0x71, 0xA2, 0x3D, 0x54, 0x18, 0xFE, 0x09
        ]

        result = [0] * 20
        for i in range(20):
            byte_val = payload[i]
            swapped = ((byte_val & 0x0F) << 4) | ((byte_val & 0xF0) >> 4)
            prev = result[i - 1] if i > 0 else 0x55
            result[i] = (swapped ^ prev ^ trans_table[i % len(trans_table)]) & 0xFF

        prefix = "8404" + "01" + "14"
        hex_body = "".join(f"{b:02x}" for b in result)
        return prefix + hex_body

    async def sign_request(self, url_query: str, body: Optional[bytes] = None, cookies: Optional[str] = None) -> Dict[str, str]:
        now_sec = int(time.time())
        now_ms = int(time.time() * 1000)
        
        gorgon = self.generate_gorgon(now_sec, url_query, body, cookies)

        return {
            "X-Gorgon": gorgon,
            "X-Khronos": str(now_sec),
            "X-SS-REQ-TICKET": str(now_ms),
            "Passport-sdk-version": "19",
            "X-SS-TC": "0",
        }

class RemoteSignerClient(BaseSigner):
    """
    Client for enterprise production signing microservices
    (e.g., Unidbg / Sekiro / Frida ARM emulator pools / TikTokSigner).
    Resolves full mobile signature suite including X-Argus and X-Ladon.
    """

    def __init__(self, signer_url: str):
        self.signer_url = signer_url.rstrip("/")

    async def sign_request(self, url_query: str, body: Optional[bytes] = None, cookies: Optional[str] = None) -> Dict[str, str]:
        now_sec = int(time.time())
        now_ms = int(time.time() * 1000)
        
        payload = {
            "query": url_query,
            "body": body.decode("latin1") if body else "",
            "cookie": cookies or "",
            "timestamp": now_sec,
        }

        try:
            async with httpx.AsyncClient(timeout=settings.SIGNER_TIMEOUT_SEC) as client:
                resp = await client.post(f"{self.signer_url}/sign", json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    
                    # Normalize response keys
                    gorgon = data.get("x_gorgon") or data.get("X-Gorgon") or data.get("gorgon")
                    khronos = str(data.get("x_khronos") or data.get("X-Khronos") or data.get("khronos") or now_sec)
                    req_ticket = str(data.get("x_ss_req_ticket") or data.get("X-SS-REQ-TICKET") or data.get("ticket") or now_ms)
                    argus = data.get("x_argus") or data.get("X-Argus") or data.get("argus")
                    ladon = data.get("x_ladon") or data.get("X-Ladon") or data.get("ladon")
                    trace_id = data.get("x_tt_trace_id") or data.get("X-TT-Trace-Id") or data.get("trace_id")

                    headers: Dict[str, str] = {
                        "X-Gorgon": gorgon or LocalGorgonSigner.generate_gorgon(int(khronos), url_query, body, cookies),
                        "X-Khronos": khronos,
                        "X-SS-REQ-TICKET": req_ticket,
                        "Passport-sdk-version": "19",
                    }
                    if argus:
                        headers["X-Argus"] = str(argus)
                    if ladon:
                        headers["X-Ladon"] = str(ladon)
                    if trace_id:
                        headers["X-TT-Trace-Id"] = str(trace_id)
                    return headers
        except Exception:
            # Resilient fallback to local Gorgon v04 signature
            local_fallback = LocalGorgonSigner()
            return await local_fallback.sign_request(url_query, body, cookies)
        
        local_fallback = LocalGorgonSigner()
        return await local_fallback.sign_request(url_query, body, cookies)

def get_signer() -> BaseSigner:
    if settings.SIGNER_MODE == "remote" and settings.REMOTE_SIGNER_URL:
        return RemoteSignerClient(settings.REMOTE_SIGNER_URL)
    return LocalGorgonSigner()
