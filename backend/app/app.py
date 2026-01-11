from flask import Flask, render_template, request, jsonify
from backend.app.controllers.light_controller import LightController
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
controller = LightController()

@app.route('/')
def index():
    return render_template('dashboard.html')

@app.route('/api/control', methods=['POST'])
def control():
    success = controller.process_command(request.json)
    if success:
        return jsonify({"status": "success"}), 200
    return jsonify({"status": "error"}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)