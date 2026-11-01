from app.services.resolver import TikTokResolver
from app.services.signer import get_signer
from app.services.aweme_client import AwemeClient
from app.services.transcoder import StickerTranscoder

def get_resolver() -> TikTokResolver:
    return TikTokResolver()

def get_aweme_client() -> AwemeClient:
    return AwemeClient(signer=get_signer())

def get_transcoder() -> StickerTranscoder:
    return StickerTranscoder()
