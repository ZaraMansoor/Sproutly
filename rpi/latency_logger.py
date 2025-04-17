from flask import Flask, request, jsonify
from datetime import datetime
import os
from OpenSSL import SSL

# app = Flask(__name__)

# # Load SSL certificates
# context = SSL.Context(SSL.SSLv23_METHOD)
# context.use_certificate_file('cert.pem')
# context.use_privatekey_file('key.pem')

# @app.route('/log-latency', methods=['POST'])
# def log_latency():
#     data = request.get_json()
#     if not data:
#         return jsonify({"status": "error", "reason": "no data"}), 400

#     try:
#         received = data['timestamp']
#         frame_ts = data['frameTimestamp']
#         latency = data['latency']
#         with open('latency_log.csv', 'a') as f:
#             f.write(f"{received},{frame_ts},{latency}\n")
#         return jsonify({"status": "ok"}), 200
#     except KeyError:
#         return jsonify({"status": "error", "reason": "missing fields"}), 400

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5001, ssl_context=context)


from flask import Flask, request
import ssl

app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def home():
    return "Welcome to the Latency Logger API!"

# Define your SSL context with the certificate and key file paths.
# Replace these with the actual paths to your certificate and private key.
context = ('./cert.pem', './key.pem')  # or 'adhoc' for self-signed cert

@app.route('/log-latency', methods=['POST'])
def log_latency():
    app.logger.info("POST request received at /log-latency")
    data = request.get_json()
    print(data)
    return {"status": "ok"}

if __name__ == '__main__':
    # Make sure you're passing the right context
    app.run(host='0.0.0.0', port=5001, ssl_context=context)
