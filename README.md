# GPChrome-Render Sidecar Server

FastAPI 기반 GPChrome 사이드카 서버.
로컬 런처 ↔ Render ↔ GPTs 간 양방향 통신을 지원.

## Features
- `/health` : Render Health Check
- `/diagnose` : Upstream 연결 확인
- `/set-upstream` : 로컬 FastAPI URL 지정
- `/report-result` : 실행 결과 보고
- `/patch-launcher` : 런처 패치
- `/update-launcher` : 런처 업데이트

## Deploy on Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
- Health Check Path: `/health`

## Environment Variables
- `UPSTREAM_URL` = http://127.0.0.1:8000
- `X_ADMIN_TOKEN` = GPChrome
