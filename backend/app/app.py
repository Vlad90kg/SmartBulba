import threading
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from pubnub_manager.activity_listener import start_activity_listener
from controllers.light_controller import LightController


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
    threading.Thread(target=start_activity_listener, daemon=True).start()
    app.run(host='0.0.0.0', port=5000)