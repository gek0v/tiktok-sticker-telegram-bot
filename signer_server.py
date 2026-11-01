"""
Signer Microservice implementing ByteDance mobile signature contract (X-Argus, X-Ladon, X-Gorgon, X-Khronos).
Adheres strictly to shared/remote_signer_spec.md contract.
"""
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from tiktok_signer import TikTokSigner

app = FastAPI(title="TikTok Mobile Remote Signer", version="1.0.0")

class SignRequest(BaseModel):
    query: str = Field(..., description="URL query string to sign")
    body: Optional[str] = Field(default="", description="Request body string if POST")
    cookie: Optional[str] = Field(default="", description="Cookie string if available")
    timestamp: Optional[int] = Field(default=None, description="Khronos timestamp in seconds")

class SignResponse(BaseModel):
    status: str = "success"
    x_gorgon: str
    x_khronos: int
    x_ss_req_ticket: int
    x_argus: Optional[str] = None
    x_ladon: Optional[str] = None
    x_tt_trace_id: Optional[str] = None

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "tiktok-remote-signer"}

@app.post("/sign", response_model=SignResponse)
async def sign_endpoint(req: SignRequest):
    try:
        ts = req.timestamp or int(time.time())
        device = TikTokSigner.get_device()
        
        headers = TikTokSigner.generate_headers(
            params=req.query,
            data=req.body.encode("utf-8") if req.body else None,
            cookie=req.cookie or None,
            unix=ts,
            device=device,
            aid=1233,
            version_name="37.0.4",
            version_code=370004
        )
        
        gorgon = headers.get("x-gorgon") or ""
        khronos = int(headers.get("x-khronos") or ts)
        req_ticket = int(headers.get("x-ss-req-ticket") or (ts * 1000))
        argus = headers.get("x-argus")
        ladon = headers.get("x-ladon")
        trace_id = headers.get("x-tt-trace-id")

        return SignResponse(
            status="success",
            x_gorgon=gorgon,
            x_khronos=khronos,
            x_ss_req_ticket=req_ticket,
            x_argus=argus,
            x_ladon=ladon,
            x_tt_trace_id=trace_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Signer generation failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8088)
