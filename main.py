import os
import httpx
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from handlers import report_handler, patch_handler, update_handler

app = FastAPI()
UPSTREAM_URL = os.getenv("UPSTREAM_URL")
ADMIN_TOKEN = os.getenv("X_ADMIN_TOKEN", "GPChrome")

@app.get("/health")
async def health():
    return {"status": "ok", "service": "sidecar"}

@app.get("/diagnose")
async def diagnose():
    if not UPSTREAM_URL:
        return {"status": "warn", "error": "UPSTREAM_URL not set"}
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{UPSTREAM_URL}/health")
            return {"status": "ok", "upstream": r.json()}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@app.post("/set-upstream")
async def set_upstream(request: Request):
    data = await request.json()
    global UPSTREAM_URL
    UPSTREAM_URL = data.get("upstream")
    return {"ok": "upstream", "value": UPSTREAM_URL}

@app.post("/report-result")
async def report_result(request: Request):
    return await report_handler.handle(request, ADMIN_TOKEN)

@app.post("/patch-launcher")
async def patch_launcher(request: Request):
    return await patch_handler.handle(request, ADMIN_TOKEN)

@app.post("/update-launcher")
async def update_launcher(request: Request):
    return await update_handler.handle(request, ADMIN_TOKEN)
