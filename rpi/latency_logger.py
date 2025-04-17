from flask import Flask, request, jsonify
from datetime import datetime
import os

app = Flask(__name__)
LOG_FILE = 'latency_log.csv'

# Make sure file has headers
if not os.path.exists(LOG_FILE):
    with open(LOG_FILE, 'w') as f:
        f.write('received_timestamp,frame_timestamp,latency_ms\n')

@app.route('/log-latency', methods=['POST'])
def log_latency():
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "reason": "no data"}), 400

    try:
        received = data['timestamp']
        frame_ts = data['frameTimestamp']
        latency = data['latency']
        with open(LOG_FILE, 'a') as f:
            f.write(f"{received},{frame_ts},{latency}\n")
        return jsonify({"status": "ok"}), 200
    except KeyError:
        return jsonify({"status": "error", "reason": "missing fields"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
