from flask import Flask, request, jsonify
from flask_cors import CORS
import spooky_engine

app = Flask(__name__)
CORS(app)

# In-memory temporary signaling store for WebRTC P2P handshakes
# (Ephemeral storage: clears out per session to maintain zero-retention)
active_signals = {}

@app.route('/transfer', methods=['POST'])
def handle_transfer():
    """Existing route to dispatch the cryptographic SES email doorbell."""
    try:
        data = request.get_json()
        email = data.get('email')
        asset_id = data.get('asset_id')
        secure_token = data.get('secure_token', 'SPKY-SECURE-NODE-LOCK-2026')
        
        success = spooky_engine.dispatch_secure_key_notification(email, secure_token, asset_id)
        
        if success:
            return jsonify({
                "status": "success", 
                "message": f"Active Spooky Key verified for [{email}]. Encrypted tunnel established."
            }), 200
        else:
            return jsonify({"status": "error", "message": "AWS SES transmission failed."}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/api/signal/offer', methods=['POST'])
def post_offer():
    """Sender posts the WebRTC connection offer linked to the Asset ID."""
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
    app.run(host='0.0.0.0', port=5000)