
from flask import Flask, request, jsonify, send_from_directory
import json, os
from datetime import datetime

app = Flask(__name__)

COMMAND_FILE = "commands.json"
UPDATE_FOLDER = "updates"

if not os.path.exists(COMMAND_FILE):
    with open(COMMAND_FILE, "w", encoding="utf-8") as f:
        json.dump({"command": None, "timestamp": None}, f)

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
