from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import traceback
import urllib.parse
import os
import json
import threading
import spooky_engine

app = Flask(__name__)
app.url_map.strict_slashes = False

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

@app.before_request
def log_incoming_requests():
    print(f"[INBOUND HIT] Method: {request.method} | Path: {request.path} | IP: {request.remote_addr}")

@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

active_signals = {}

@app.route('/', methods=['GET', 'OPTIONS'])
def home():
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    receive_asset = request.args.get('receive')
    
    if receive_asset:
        return f"""
        <html>
          <head>
            <title>Spooky Sovereign P2P Receiver Gateway</title>
          </head>
          <body style="background-color: #07080a; color: #00ff66; font-family: monospace; padding: 40px;">
            <h2>SPOOKY SOVEREIGN P2P RECEIVER GATEWAY</h2>
            <p>Target Asset Identified: <strong>{receive_asset}</strong></p>
            <p>Ready to establish direct WebRTC encrypted tunnel with the sender node.</p>
            <div style="margin-top: 20px; padding: 15px; border: 1px solid #00ff66; background: #1a1e29;">
              <p>Receiver signaling interface active. Zero-retention protocol engaged.</p>
              <button onclick="initiateP2PDownload('{receive_asset}')" style="background: #00ff66; color: #0d0d0d; padding: 12px 20px; border: none; font-weight: bold; cursor: pointer; margin-top: 15px; font-family: monospace;">
                Establish P2P Tunnel & Download File
              </button>
              <p id="status-log" style="margin-top: 15px; color: #fff;"></p>
            </div>
            <script>
              async function initiateP2PDownload(assetId) {{
                const statusLog = document.getElementById('status-log');
                statusLog.innerText = "Querying signaling switchboard for WebRTC offer...";
                try {{
                  const response = await fetch('https://spookyfied.com/api/signal/offer/' + encodeURIComponent(assetId));
                  if (!response.ok) {{
                    throw new Error("Signaling offer not found or expired on switchboard.");
                  }}
                  const data = await response.json();
                  statusLog.innerText = "Offer acquired! Establishing peer connection & generating answer...";
                  
                  const pc = new RTCPeerConnection({{'iceServers': [{{'urls': 'stun:stun.l.google.com:19302'}}]}});
                  
                  pc.ondatachannel = (event) => {{
                    const channel = event.channel;
                    statusLog.innerText = "Data channel open! Receiving file payload across direct P2P tunnel...";
                    let receivedChunks = [];
                    
                    channel.onmessage = (e) => {{
                      if (typeof e.data === 'string' && e.data.startsWith('EOF:')) {{
                        const blob = new Blob(receivedChunks);
                        const url = URL.createObjectURL(blob);
                        const a = document.createElement('a');
                        a.href = url;
                        a.download = assetId.replace('.spooky', '');
                        document.body.appendChild(a);
                        a.click();
                        statusLog.innerText = "SUCCESS: File successfully received and decrypted locally!";
                      }} else {{
                        receivedChunks.push(e.data);
                      }}
                    }};
                  }};
                  
                  await pc.setRemoteDescription(new RTCSessionDescription(data.offer));
                  const answer = await pc.createAnswer();
                  await pc.setLocalDescription(answer);
                  
                  await fetch('https://spookyfied.com/api/signal/answer', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ asset_id: assetId, answer: answer }})
                  }});
                  
                  statusLog.innerText = "Answer dispatched to switchboard. Awaiting direct stream from sender node...";
                }} catch (err) {{
                  statusLog.innerText = "Error: " + err.message;
                }}
              }}
            </script>
          </body>
        </html>
        """, 200
        
    return "Spooky Sovereign Backend Gateway Online. Use frontend portal at spookyfied.com.", 200

@app.route('/transfer', methods=['POST', 'OPTIONS'])
def handle_transfer():
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    try:
        # Support both multipart form-data (from index.html file upload) and JSON payloads
        if request.is_json:
            data = request.json or {}
            email = data.get('email')
            filename = data.get('filename')
            offer = data.get('offer')
            secure_token = data.get('secure_token', 'SPKY-SECURE-NODE-LOCK-2026')
        else:
            email = request.form.get('email')
            uploaded_file = request.files.get('file')
            filename = uploaded_file.filename if uploaded_file else request.form.get('filename')
            offer_raw = request.form.get('offer')
            offer = json.loads(offer_raw) if offer_raw else {"type": "offer", "sdp": "mock-direct-stream-sdp"}
            secure_token = request.form.get('secure_token', 'SPKY-SECURE-NODE-LOCK-2026')
        
        print(f"[TRANSFER DEBUG] Email: {email} | Filename: {filename} | Offer present: {bool(offer)}")
        
        if not email or not filename:
            return jsonify({"status": "error", "message": "Missing parameters in transfer payload."}), 400
            
        asset_id = filename + ".spooky"
        active_signals[asset_id] = {
            'offer': offer or {},
            'answer': None,
            'sender_candidates': [],
            'receiver_candidates': []
        }
        
        download_url = f"https://spookyfied.com/?receive={urllib.parse.quote(asset_id)}"
        
        def async_ses_dispatch():
            try:
                spooky_engine.dispatch_secure_key_notification(
                    recipient_email=email, 
                    secure_key_token=secure_token, 
                    asset_id=asset_id, 
                    download_url=download_url
                )
            except Exception as e:
                print(f"[SES ASYNC ERROR] {e}")

        thread = threading.Thread(target=async_ses_dispatch)
        thread.start()
        
        return jsonify({"status": "success", "message": f"Active Spooky Key verified for [{email}]. Encrypted tunnel established."}), 200
            
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signal/offer/<asset_id>', methods=['GET', 'OPTIONS'])
def get_offer(asset_id):
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    signal_data = active_signals.get(asset_id)
    if not signal_data:
        return jsonify({"error": "Offer not found or expired"}), 404
    return jsonify(signal_data), 200

@app.route('/api/signal/answer', methods=['POST', 'OPTIONS'])
def post_answer():
    if request.method == 'OPTIONS':
        return make_response('', 200)
        
    try:
        data = request.json or {}
        asset_id = data.get('asset_id')
        answer = data.get('answer')
        
        if not asset_id or not answer:
            return jsonify({"status": "error", "message": "Missing parameters."}), 400
            
        if asset_id in active_signals:
            active_signals[asset_id]['answer'] = answer
            return jsonify({"status": "answer_stored"}), 200
            
        return jsonify({"error": "Session not found"}), 404
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)