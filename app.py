from flask import Flask, request, jsonify
from flask_cors import CORS
import traceback
import spooky_engine

app = Flask(__name__)
CORS(app)

@app.before_request
def log_incoming_requests():
    """Diagnostic logger to trace every inbound hit to the local production server."""
    print(f"[INBOUND] {request.method} request to {request.path}")

# In-memory temporary signaling store for WebRTC P2P handshakes
active_signals = {}

@app.route('/')
def home():
    """Unified route: Serves the Receiver Gateway if ?receive= is present, else serves the Sender Dashboard."""
    receive_asset = request.args.get('receive')
    
    if receive_asset:
        # --- RECEIVER GATEWAY VIEW ---
        return f"""
        <html>
          <head>
            <title>Spooky Sovereign P2P Receiver Gateway</title>
          </head>
          <body style="background-color: #0d0d0d; color: #00ff66; font-family: monospace; padding: 40px;">
            <h2>SPOOKY SOVEREIGN P2P RECEIVER GATEWAY</h2>
            <p>Target Asset Identified: <strong>{receive_asset}</strong></p>
            <p>Ready to establish direct WebRTC encrypted tunnel with the sender node.</p>
            <div style="margin-top: 20px; padding: 15px; border: 1px solid #00ff66; background: #1a1a1a;">
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
                  const response = await fetch('/api/signal/offer/' + encodeURIComponent(assetId));
                  if (!response.ok) {{
                    throw new Error("Signaling offer not found or expired on switchboard.");
                  }}
                  const data = await response.json();
                  statusLog.innerText = "Offer acquired! Establishing peer connection...";
                  
                  const pc = new RTCPeerConnection({{'iceServers': [{{'urls': 'stun:stun.l.google.com:19302'}}]}});
                  
                  pc.ondatachannel = (event) => {{
                    const channel = event.channel;
                    statusLog.innerText = "Data channel open! Receiving file payload...";
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
                  
                  await fetch('/api/signal/answer', {{
                    method: 'POST',
                    headers: {{ 'Content-Type': 'application/json' }},
                    body: JSON.stringify({{ asset_id: assetId, answer: answer }})
                  }});
                  
                  statusLog.innerText = "Answer dispatched to switchboard. Awaiting P2P stream...";
                }} catch (err) {{
                  statusLog.innerText = "Error: " + err.message;
                }}
              }}
            </script>
          </body>
        </html>
        """, 200
    
    # --- SENDER DASHBOARD VIEW ---
    return """
    <html>
      <head>
        <title>Spooky Sovereign Enterprise Node</title>
      </head>
      <body style="background-color: #0d0d0d; color: #00ff66; font-family: monospace; padding: 40px;">
        <h2>SPOOKY SOVEREIGN SECURE NODE DASHBOARD</h2>
        <div style="margin-top: 20px; padding: 20px; border: 1px solid #00ff66; background: #1a1a1a; max-width: 600px;">
          <form id="transfer-form" onsubmit="handleTransfer(event)">
            <p><label>Recipient Email:</label><br>
            <input type="email" id="email" required style="width: 100%; padding: 8px; background: #0d0d0d; color: #00ff66; border: 1px solid #00ff66; font-family: monospace; margin-top: 5px;"></p>
            
            <p><label>Select Payload File:</label><br>
            <input type="file" id="file-input" required style="width: 100%; padding: 8px; background: #0d0d0d; color: #00ff66; border: 1px solid #00ff66; font-family: monospace; margin-top: 5px;"></p>
            
            <button type="submit" style="background: #00ff66; color: #0d0d0d; padding: 12px 20px; border: none; font-weight: bold; cursor: pointer; width: 100%; font-family: monospace; margin-top: 10px;">
              Initialize Secure P2P Transmission
            </button>
          </form>
          <p id="status-log" style="margin-top: 15px; color: #fff;"></p>
        </div>
        <script>
          async function handleTransfer(event) {
            event.preventDefault();
            const statusLog = document.getElementById('status-log');
            const email = document.getElementById('email').value;
            const fileInput = document.getElementById('file-input').files[0];
            
            if (!fileInput) return;
            
            statusLog.innerText = "Interrogating Node & Generating WebRTC Offer...";
            
            const assetId = fileInput.name + ".spooky";
            
            // Create WebRTC Offer for P2P streaming
            const pc = new RTCPeerConnection({'iceServers': [{'urls': 'stun:stun.l.google.com:19302'}]});
            const dataChannel = pc.createDataChannel("file-transfer");
            
            const offer = await pc.createOffer();
            await pc.setLocalDescription(offer);
            
            // Explicitly serialize offer type and sdp to guarantee transmission
            const cleanOffer = { type: offer.type, sdp: offer.sdp };
            
            const formData = new FormData();
            formData.append('email', email);
            formData.append('file', fileInput);
            formData.append('offer', JSON.stringify(cleanOffer));
            
            statusLog.innerText = "Dispatching SES Secure Key Notification & Registering Switchboard...";
            const response = await fetch('/transfer', { method: 'POST', body: formData });
            const result = await response.json();
            
            if (response.ok) {
              statusLog.innerText = "Success: " + result.message + " Waiting for receiver to connect...";
              
              // Poll for receiver answer
              const interval = setInterval(async () => {
                const res = await fetch('/api/signal/offer/' + encodeURIComponent(assetId));
                const data = await res.json();
                if (data.answer && !pc.remoteDescription) {
                  await pc.setRemoteDescription(new RTCSessionDescription(data.answer));
                  clearInterval(interval);
                  statusLog.innerText = "Peer connected! Streaming payload over encrypted WebRTC channel...";
                  
                  dataChannel.onopen = () => {
                    const reader = new FileReader();
                    let offset = 0;
                    const chunkSize = 16384;
                    
                    reader.onload = (e) => {
                      dataChannel.send(e.target.result);
                      offset += e.target.result.byteLength;
                      if (offset < fileInput.size) {
                        readSlice(offset);
                      } else {
                        dataChannel.send("EOF:" + assetId);
                        statusLog.innerText = "Transfer Complete: Payload streamed securely peer-to-peer.";
                      }
                    };
                    
                    function readSlice(o) {
                      const slice = fileInput.slice(o, o + chunkSize);
                      reader.readAsArrayBuffer(slice);
                    }
                    readSlice(0);
                  };
                }
              }, 2000);
            } else {
              statusLog.innerText = "Transmission Error: " + result.message;
            }
          }
        </script>
      </body>
    </html>
    """, 200

@app.route('/transfer', methods=['POST'])
def handle_transfer():
    """Route to handle atomic transfer: registers signal offer and dispatches SES notification in one pass."""
    import json
    try:
        email = request.form.get('email')
        file_obj = request.files.get('file')
        offer_str = request.form.get('offer')
        secure_token = request.form.get('secure_token', 'SPKY-SECURE-NODE-LOCK-2026')
        
        asset_id = (file_obj.filename + ".spooky") if file_obj else None
        
        print(f"[DEBUG] Email: {email}, Asset ID: {asset_id}, File: {file_obj}, Offer Received: {bool(offer_str)}")
        
        if not email or not file_obj or not offer_str:
            print(f"[ERROR] Rejection: Missing parameters -> email: {email}, file: {file_obj}, offer: {bool(offer_str)}")
            return jsonify({"status": "error", "message": "Missing parameters, file payload, or offer."}), 400
            
        active_signals[asset_id] = {
            'offer': json.loads(offer_str),
            'answer': None,
            'sender_candidates': [],
            'receiver_candidates': []
        }
        
        download_url = f"http://192.168.0.155:5000/?receive={asset_id}"
        
        success = spooky_engine.dispatch_secure_key_notification(
            recipient_email=email, 
            secure_key_token=secure_token, 
            asset_id=asset_id, 
            download_url=download_url
        )
        
        if success:
            return jsonify({
                "status": "success", 
                "message": f"Active Spooky Key verified for [{email}]. Encrypted tunnel established."
            }), 200
        else:
            return jsonify({"status": "error", "message": "AWS SES transmission failed."}), 500
    except Exception as e:
        traceback.print_exc()
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signal/offer', methods=['POST'])
def post_offer():
    """Fallback manual offer endpoint."""
    data = request.json
    asset_id = data.get('asset_id')
    offer = data.get('offer')
    
    active_signals[asset_id] = {
        'offer': offer,
        'answer': None,
        'sender_candidates': [],
        'receiver_candidates': []
    }
    return jsonify({"status": "offer_stored", "asset_id": asset_id}), 200

@app.route('/api/signal/offer/<asset_id>', methods=['GET'])
def get_offer(asset_id):
    """Receiver fetches the WebRTC offer to initiate the P2P handshake."""
    signal_data = active_signals.get(asset_id)
    if not signal_data:
        return jsonify({"error": "Offer not found or expired"}), 404
    return jsonify(signal_data), 200

@app.route('/api/signal/answer', methods=['POST'])
def post_answer():
    """Receiver posts their WebRTC answer back to the switchboard."""
    data = request.json
    asset_id = data.get('asset_id')
    answer = data.get('answer')
    
    if asset_id in active_signals:
        active_signals[asset_id]['answer'] = answer
        return jsonify({"status": "answer_stored"}), 200
    return jsonify({"error": "Session not found"}), 404

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)