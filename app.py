from flask import Flask, request, jsonify, render_template_string, send_from_directory
import json, os, base64
from datetime import datetime

app = Flask(__name__)

# ===============================
# 📂 폴더 및 파일 경로 설정
# ===============================
COMMAND_FILE = "commands.json"
LOG_FILE = "commands_log.json"
STATUS_FILE = "status.json"
STATUS_LOG_FILE = "status_log.json"
UPDATE_FOLDER = "updates"        # 업데이트 파일 다운로드 경로
UPLOAD_DIR = "uploads"           # 새 파일 업로드 경로 (ChatGPT → Render)

os.makedirs(UPDATE_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ✅ 서버 초기화 시 JSON 파일이 없으면 생성
for file_path, default in [
    (COMMAND_FILE, {"command": None, "type": None, "timestamp": None}),
    (LOG_FILE, []),
    (STATUS_FILE, {"status": None, "timestamp": None}),
    (STATUS_LOG_FILE, [])
]:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default, f)

# ===============================
# 🖥 Admin 웹페이지 HTML 템플릿
# ===============================
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>GPChrome Admin</title></head>
<body style="font-family: Arial; margin:40px;">
<h2>🛠 GPChrome 명령 전송 & 모니터링</h2>
<form method="POST" action="/admin">
    <label>명령 유형:</label>
    <select name="type">
        <option value="general">General</option>
        <option value="crawl">Crawl</option>
        <option value="capture">Capture</option>
        <option value="github">GitHub</option>
    </select>
    <input type="text" name="command" placeholder="명령 입력" style="width:300px; height:30px;">
    <button type="submit" style="height:36px;">전송</button>
</form>
<hr>
<h3>현재 명령</h3>
<p>Type: <b>{{ current_type }}</b> | Command: <b>{{ current_command }}</b> | Time: {{ cmd_time }}</p>
<hr>
<h3>Command Log</h3>
<table border="1" cellpadding="4" style="border-collapse: collapse;">
    <tr><th>Time</th><th>Type</th><th>Command</th></tr>
    {% for entry in log %}
    <tr><td>{{ entry.timestamp }}</td><td>{{ entry.type }}</td><td>{{ entry.command }}</td></tr>
    {% endfor %}
</table>
<hr>
<h3>Status Log</h3>
<table border="1" cellpadding="4" style="border-collapse: collapse;">
    <tr><th>Time</th><th>Status</th></tr>
    {% for entry in status_log %}
    <tr><td>{{ entry.timestamp }}</td><td>{{ entry.status }}</td></tr>
    {% endfor %}
</table>
</body>
</html>
'''

# ===============================
# ✅ Admin 페이지
# ===============================
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        cmd = request.form.get("command")
        cmd_type = request.form.get("type")
        ts = datetime.now().isoformat()

        # 명령 파일 업데이트
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            json.dump({"command": cmd, "type": cmd_type, "timestamp": ts}, f)

        # 명령 로그 추가
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            log = json.load(f)
            log.append({"command": cmd, "type": cmd_type, "timestamp": ts})
            f.seek(0)
            json.dump(log, f)

    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        current = json.load(f)
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status = json.load(f)
    with open(STATUS_LOG_FILE, "r", encoding="utf-8") as f:
        status_log = json.load(f)

    return render_template_string(ADMIN_HTML,
                                  current_command=current.get("command"),
                                  current_type=current.get("type"),
                                  cmd_time=current.get("timestamp"),
                                  log=log,
                                  status_log=status_log)

# ===============================
# ✅ 명령 API (GET/POST)
# ===============================
@app.route('/command', methods=['GET'])
def get_cmd():
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route('/command', methods=['POST'])
def post_cmd():
    data = request.json
    cmd = data.get("command")
    typ = data.get("type")
    ts = datetime.now().isoformat()

    # ✅ update 명령 실행 중이면 덮어쓰기 방지
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        current = json.load(f)
    if current.get("command") and str(current.get("command")).startswith("update:") and cmd not in [None, ""]:
        return jsonify({"status": "locked", "message": "update 명령 실행 중, 덮어쓰기 차단됨"})

    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"command": cmd, "type": typ, "timestamp": ts}, f)

    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        log = json.load(f)
        log.append({"command": cmd, "type": typ, "timestamp": ts})
        f.seek(0)
        json.dump(log, f)

    return jsonify({"status": "ok"})

# ===============================
# ✅ 상태 API (POST/GET)
# ===============================
@app.route('/status', methods=['POST'])
def post_status():
    data = request.json
    st = data.get("status")
    ts = datetime.now().isoformat()

    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({"status": st, "timestamp": ts}, f)

    with open(STATUS_LOG_FILE, "r+", encoding="utf-8") as f:
        slog = json.load(f)
        slog.append({"status": st, "timestamp": ts})
        f.seek(0)
        json.dump(slog, f)

    return jsonify({"status": "updated"})

@app.route('/status', methods=['GET'])
def get_status():
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

# ===============================
# ✅ 업데이트 파일 다운로드 (기존 유지)
# ===============================
@app.route('/update/<filename>', methods=['GET'])
def download_update(filename):
    return send_from_directory(UPDATE_FOLDER, filename, as_attachment=True)

# ===============================
# 🆕 새 파일 업로드 API (ChatGPT → Render)
# ===============================
@app.route('/upload', methods=['POST'])
def upload_file():
    """
    파일 조각(chunk) 업로드
    - filename: 저장할 파일명
    - chunk: Base64 인코딩된 파일 조각
    - index: 현재 조각 번호
    - total: 전체 조각 수
    """
    data = request.json
    filename = data.get("filename")
    chunk = data.get("chunk")
    index = data.get("index")
    total = data.get("total")

    if not filename or chunk is None:
        return jsonify({"status": "error", "msg": "filename or chunk missing"}), 400

    # 조각 저장용 폴더 생성
    chunk_folder = os.path.join(UPLOAD_DIR, f"{filename}_chunks")
    os.makedirs(chunk_folder, exist_ok=True)

    # Base64 → 바이너리 변환 후 조각 저장
    chunk_path = os.path.join(chunk_folder, f"{index}.part")
    with open(chunk_path, "wb") as f:
        f.write(base64.b64decode(chunk))

    # 마지막 조각이면 → 파일 합치기
    if index == total - 1:
        output_path = os.path.join(UPLOAD_DIR, filename)
        with open(output_path, "wb") as outfile:
            for i in range(total):
                part_path = os.path.join(chunk_folder, f"{i}.part")
                with open(part_path, "rb") as infile:
                    outfile.write(infile.read())

        # 조각 정리
        for i in range(total):
            os.remove(os.path.join(chunk_folder, f"{i}.part"))
        os.rmdir(chunk_folder)

    return jsonify({"status": "ok", "msg": f"chunk {index} received"})

# ===============================
# ✅ 기본 홈 경로
# ===============================
@app.route('/')
def home():
    return "GPChrome Render Server with Monitoring & Upload API", 200

# ===============================
# ✅ 메인 실행 (로컬 테스트용)
# ===============================
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
