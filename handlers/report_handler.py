from fastapi import Request
from fastapi.responses import JSONResponse

async def handle(request: Request, admin_token: str):
    try:
        body = await request.json()
        token = request.headers.get("x-admin-token", "")
        if token != admin_token:
            return JSONResponse({"error": "unauthorized"}, status_code=403)
        return JSONResponse({"status": "received", "report": body}, status_code=200)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
