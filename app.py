
from flask import Flask, request, jsonify, send_from_directory, render_template_string
import json, os
from datetime import datetime

app = Flask(__name__)

COMMAND_FILE = "commands.json"
UPDATE_FOLDER = "updates"

if not os.path.exists(COMMAND_FILE):
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"command": None, "timestamp": None}, f)

# 관리자 페이지 HTML
ADMIN_HTML = '''
<!DOCTYPE html>
<html>
<head><title>GPChrome Admin</title></head>
<body style="font-family: Arial; margin:40px;">
<h2>🛠 GPChrome 명령 전송</h2>
<form method="POST" action="/admin">
    <input type="text" name="command" placeholder="명령 입력" style="width:300px; height:30px;">
    <button type="submit" style="height:36px;">전송</button>
</form>
<hr>
<p>현재 명령: <b>{{ current_command }}</b></p>
<p>최근 업데이트: {{ timestamp }}</p>
</body>
</html>
'''

@app.route('/admin', methods=['GET', 'POST'])
def admin_page():
    if request.method == 'POST':
        cmd = request.form.get("command")
        with open(COMMAND_FILE, "w", encoding="utf-8") as f:
            json.dump({"command": cmd, "timestamp": datetime.now().isoformat()}, f)
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return render_template_string(ADMIN_HTML, current_command=data.get("command"), timestamp=data.get("timestamp"))

@app.route('/command', methods=['GET'])
def get_command():
    with open(COMMAND_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)

@app.route('/command', methods=['POST'])
def set_command():
    data = request.json
    new_command = data.get("command")
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"command": new_command, "timestamp": datetime.now().isoformat()}, f)
    return jsonify({"status": "ok", "command": new_command})

@app.route('/update/<filename>', methods=['GET'])
def download_update(filename):
    return send_from_directory(UPDATE_FOLDER, filename, as_attachment=True)

@app.route('/')
def home():
    return "✅ Render Flask Server Running", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
