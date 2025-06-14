# utils/security.py (or similar)
from fastapi import Request, HTTPException, status

MAX_PAYLOAD_BYTES = 50_000   # 50 KB, tune as you like

async def enforce_payload_size(request: Request):
    cl = request.headers.get("content-length")
    if cl and int(cl) > MAX_PAYLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Payload too large (max {MAX_PAYLOAD_BYTES} bytes)",
        )
    body = await request.body()
    if len(body) > MAX_PAYLOAD_BYTES:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Payload too large")