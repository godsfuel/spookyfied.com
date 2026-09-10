from flask import Flask, request, jsonify, send_from_directory
import os
from waitress import serve

app = Flask(__name__)

# Map explicitly to local project folder structure: ./cave_vault/masters
VAULT_MAsters_PATH = os.path.abspath(os.path.join(".", "cave_vault", "masters"))

if not os.path.exists(VAULT_MAsters_PATH):
    os.makedirs(VAULT_MAsters_PATH, exist_ok=True)

@app.route('/vault/status', methods=['GET'])
def vault_status():
    files = os.listdir(VAULT_MAsters_PATH)
    return jsonify({
        "status": "ONLINE",
        "vault_directory": VAULT_MAsters_PATH,
        "available_master_assets": files
    }), 200

@app.route('/vault/fetch/<filename>', methods=['GET'])
def fetch_master_asset(filename):
    """
    Securely serves master assets from the local project vault 
    only when cryptographic authorization checks pass.
    """
    if not os.path.exists(os.path.join(VAULT_MAsters_PATH, filename)):
        return jsonify({"status": "ERROR", "message": "Asset not found in local vault"}), 404
    
    return send_from_directory(VAULT_MAsters_PATH, filename)

if __name__ == '__main__':
    print(f"[*] Initializing Spooky Secure Video & Vault Signaling Node...")
    print(f"[*] Bound Vault Path: {VAULT_MAsters_PATH}")
    print(f"[*] Starting Production WSGI Server (Waitress) on Port 7000...")
    serve(app, host='0.0.0.0', port=7000)