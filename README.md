# GPChrome-Render

FastAPI + Uvicorn proxy service for GPChrome automation.

## Run locally
```bash
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## Deploy on Render
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Health Check Path:** `/health`
- **Environment Variables:**
  - `UPSTREAM_URL` = http://127.0.0.1:8000 (또는 실제 대상 서버 주소)
