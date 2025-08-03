from flask import Flask, request, jsonify, render_template_string, send_from_directory
import json, os
from datetime import datetime

app = Flask(__name__)

# File paths
COMMAND_FILE = "commands.json"
LOG_FILE = "commands_log.json"
STATUS_FILE = "status.json"
STATUS_LOG_FILE = "status_log.json"
UPDATE_FOLDER = "updates"

# Initialize files if missing
for file_path, default in [
    (COMMAND_FILE, {"command": None, "type": None, "timestamp": None}),
    (LOG_FILE, []),
    (STATUS_FILE, {"status": None, "timestamp": None}),
    (STATUS_LOG_FILE, [])
]:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default, f)

# Admin page template with AJAX polling
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head>
  <title>GPChrome Admin</title>
  <meta charset="utf-8">
  <style>
    body { font-family: Arial; margin:40px; }
    table { border-collapse: collapse; width: 100%; margin-bottom: 40px; }
    th, td { border: 1px solid #ccc; padding: 8px; text-align: left; }
  </style>
</head>
<body>
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
<table>
    <tr><th>Time</th><th>Type</th><th>Command</th></tr>
    {% for entry in log %}
    <tr><td>{{ entry.timestamp }}</td><td>{{ entry.type }}</td><td>{{ entry.command }}</td></tr>
    {% endfor %}
</table>
<hr>
<h3>Status Log (실시간 업데이트)</h3>
<table>
    <tr><th>Time</th><th>Status</th></tr>
    <tbody id="status-log">
        {% for entry in status_log %}
        <tr><td>{{ entry.timestamp }}</td><td>{{ entry.status }}</td></tr>
        {% endfor %}
    </tbody>
</table>

<script>
// 5초마다 /status_log 데이터를 새로 가져와 테이블에 추가
async function fetchNewStatus() {
    const res = await fetch('/status');
    const data = await res.json();
    const tbody = document.getElementById('status-log');
    // 이미 가장 최근 항목과 동일하면 추가하지 않음
    if (!tbody.firstChild || tbody.firstChild.firstChild.innerText !== data.timestamp) {
        const tr = document.createElement('tr');
        tr.innerHTML = `<td>${data.timestamp}</td><td>${data.status}</td>`;
        tbody.insertBefore(tr, tbody.firstChild);
    }
}
setInterval(fetchNewStatus, 5000);
</script>
</body>
</html>
'''

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        cmd = request.form.get("command")
        cmd_type = request.form.get("type")
        ts = datetime.now().isoformat()
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            json.dump({"command": cmd, "type": cmd_type, "timestamp": ts}, f)
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            log = json.load(f)
            log.append({"command": cmd, "type": cmd_type, "timestamp": ts})
            f.seek(0)
            json.dump(log, f)
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        current = json.load(f)
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
    with open(STATUS_LOG_FILE, "r", encoding="utf-8") as f:
        status_log = json.load(f)
    return render_template_string(ADMIN_HTML,
                                  current_command=current.get("command"),
                                  current_type=current.get("type"),
                                  cmd_time=current.get("timestamp"),
                                  log=log,
                                  status_log=status_log)

@app.route('/command', methods=['GET'])
def get_cmd():
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

@app.route('/status', methods=['GET'])
def get_status():
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        return jsonify(json.load(f))

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
    return jsonify({"status":"updated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
