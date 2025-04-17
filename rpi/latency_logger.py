from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import ssl

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Define the home route
@app.route('/', methods=['GET', 'POST'])
def home():
    return "Welcome to the Latency Logger API!"

# Route to log latency
@app.route('/log-latency', methods=['POST'])
def log_latency():
    data = request.get_json()
    
    if not data:
        return jsonify({"status": "error", "reason": "no data"}), 400

    try:
        received = data['timestamp']
        frame_ts = data['frameTimestamp']
        latency = data['latency']
        
        # Open the CSV file and append latency data
        with open('latency_log.csv', 'a') as f:
            f.write(f"{received},{frame_ts},{latency}\n")
        
        return jsonify({"status": "ok"}), 200
    except KeyError as e:
        # Return error if missing keys
        return jsonify({"status": "error", "reason": f"missing field: {str(e)}"}), 400

if __name__ == '__main__':
    # SSL context (ensure paths are correct or use 'adhoc' for self-signed cert)
    context = ('./cert.pem', './key.pem')
    app.run(host='0.0.0.0', port=5001, ssl_context=context)
