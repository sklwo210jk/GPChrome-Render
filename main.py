import os
import httpx
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

UPSTREAM_URL = os.getenv("UPSTREAM_URL")

# Render Health Check (항상 200 OK 보장)
@app.get("/health")
async def health():
    return JSONResponse({"status": "ok", "service": "render"}, status_code=200)

# Diagnose Endpoint (Upstream 연결 확인용)
@app.get("/diagnose")
async def diagnose():
    if not UPSTREAM_URL:
        return JSONResponse(
            {"status": "warn", "error": "UPSTREAM_URL not set"},
            status_code=200,
        )
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{UPSTREAM_URL}/health")
            return JSONResponse(
                {"status": "ok", "service": "render", "upstream": r.json()},
                status_code=200,
            )
    except Exception as e:
        return JSONResponse(
            {"status": "error", "error": str(e)},
            status_code=200,
        )
