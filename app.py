from flask import Flask, request, jsonify

app = Flask(__name__)

commands = []
results = []

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    commands.append(data)
    return jsonify({"status": "command added"})

@app.route('/get_command', methods=['GET'])
def get_command():
    if commands:
        return jsonify(commands.pop(0))
    return jsonify({})

@app.route('/send_result', methods=['POST'])
def send_result():
    data = request.json
    results.append(data)
    return jsonify({"status": "result added"})

@app.route('/get_result', methods=['GET'])
def get_result():
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
