
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)

# File paths
COMMAND_FILE = "commands.json"
LOG_FILE = "commands_log.json"
STATUS_FILE = "status.json"
UPDATE_FOLDER = "updates"

# Initialize files
for file_path, default in [(COMMAND_FILE, {"command": None, "type": None, "timestamp": None}),
                           (LOG_FILE, []),
                           (STATUS_FILE, {"status": None, "timestamp": None})]:
    if not os.path.exists(file_path):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(default, f)

# Admin page HTML
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>GPChrome Admin</title></head>
<body style="font-family: Arial; margin:40px;">
<h2>🛠 GPChrome 명령 전송</h2>
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
<h3>Last Status</h3>
<p>Status: <b>{{ last_status }}</b> | Time: {{ status_time }}</p>
</body>
</html>
'''

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        cmd = request.form.get("command")
        cmd_type = request.form.get("type")
        timestamp = datetime.now().isoformat()
        # Update command file
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            json.dump({"command": cmd, "type": cmd_type, "timestamp": timestamp}, f)
        # Append to log
        with open(LOG_FILE, "r+", encoding="utf-8") as f:
            log = json.load(f)
            log.append({"command": cmd, "type": cmd_type, "timestamp": timestamp})
            f.seek(0)
            json.dump(log, f)
    # Load data for display
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        current = json.load(f)
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        log = json.load(f)
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        status = json.load(f)
    return render_template_string(ADMIN_HTML,
                                  current_command=current.get("command"),
                                  current_type=current.get("type"),
                                  cmd_time=current.get("timestamp"),
                                  log=log,
                                  last_status=status.get("status"),
                                  status_time=status.get("timestamp"))

@app.route('/command', methods=['GET'])
def get_command():
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/command', methods=['POST'])
def set_command():
    data = request.json
    new_command = data.get("command")
    new_type = data.get("type")
    timestamp = datetime.now().isoformat()
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"command": new_command, "type": new_type, "timestamp": timestamp}, f)
    # Log it
    with open(LOG_FILE, "r+", encoding="utf-8") as f:
        log = json.load(f)
        log.append({"command": new_command, "type": new_type, "timestamp": timestamp})
        f.seek(0)
        json.dump(log, f)
    return jsonify({"status": "ok", "command": new_command, "type": new_type})

@app.route('/status', methods=['POST'])
def update_status():
    data = request.json
    status = data.get("status")
    timestamp = datetime.now().isoformat()
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump({"status": status, "timestamp": timestamp}, f)
    return jsonify({"status": "updated"})

@app.route('/status', methods=['GET'])
def get_status():
    with open(STATUS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/update/<filename>', methods=['GET'])
def download_update(filename):
    return send_from_directory(UPDATE_FOLDER, filename, as_attachment=True)

@app.route('/')
def home():
    return "✅ Render Flask Server with Admin UI and Logs Running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
