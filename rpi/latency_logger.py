from flask import Flask, request, jsonify
from flask_cors import CORS
import ssl
from datetime import datetime

app = Flask(__name__)
CORS(app)

@app.route('/', methods=['GET', 'POST'])
def home():
    return "Welcome to the Latency Logger API!"

@app.route('/log-latency', methods=['POST'])
def log_latency():
    data = request.get_json()

    if not data:
        return jsonify({"status": "error", "reason": "no data"}), 400

    try:
        received_iso = data['timestamp']
        frame_ts_str = data['frameTimestamp']

        received_dt = datetime.fromisoformat(received_iso.replace("Z", "+00:00"))
        received_str = received_dt.strftime('%H:%M:%S.%f')[:-3]

        h, m, s_ms = frame_ts_str.split(':')
        s, ms = s_ms.split('.')
        frame_dt = received_dt.replace(hour=int(h), minute=int(m), second=int(s), microsecond=int(ms) * 1000)

        latency = int((received_dt - frame_dt).total_seconds() * 1000)

        with open('latency_log.csv', 'a') as f:
            f.write(f"{received_str},{frame_ts_str},{latency}\n")

        return jsonify({"status": "ok", "latency": latency}), 200

    except KeyError as e:
        return jsonify({"status": "error", "reason": f"missing field: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"status": "error", "reason": str(e)}), 400

if __name__ == '__main__':
    context = ('./cert.pem', './key.pem')
    app.run(host='0.0.0.0', port=5001, ssl_context=context)
