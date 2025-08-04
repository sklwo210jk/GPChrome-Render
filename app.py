import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("API_KEY", "")

commands = []
results = []

def check_auth():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith('Bearer '):
        return False
    token = auth_header.split(' ')[1]
    return token == API_KEY

@app.route('/api/commands', methods=['POST'])
def add_command():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    commands.append(data)
    return jsonify({"status": "command added", "command": data})

@app.route('/api/commands', methods=['GET'])
def get_command():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    if commands:
        return jsonify(commands.pop(0))
    return jsonify({})

@app.route('/api/results', methods=['POST'])
def add_result():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    if not data:
        return jsonify({"error": "Invalid data"}), 400
    results.append(data)
    return jsonify({"status": "result added", "result": data})

@app.route('/api/results', methods=['GET'])
def get_results():
    if not check_auth():
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(results)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
