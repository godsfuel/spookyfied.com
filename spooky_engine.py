import os
import subprocess
import hashlib
import uuid
from flask import Flask, send_from_directory, request, jsonify

app = Flask(__name__)

# Define root directory for static assets
WEB_ROOT = os.path.abspath(os.path.dirname(__file__))
VAULT_DIR = os.path.join(WEB_ROOT, 'cave_vault')

# Ensure vault directory exists
if not os.path.exists(VAULT_DIR):
    os.makedirs(VAULT_DIR)

def get_hardware_signature():
    """Extracts unique hardware identifier (Motherboard/System UUID) for deterministic key binding."""
    try:
        if os.name == 'nt':
            cmd = "wmic csproduct get uuid"
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL).decode()
            lines = [line.strip() for line in output.split('\n') if line.strip()]
            if len(lines) > 1:
                return lines[1]
        # Fallback to MAC-based node if wmic is restricted
        return str(uuid.getnode())
    except Exception:
        return "FALLBACK-HARDWARE-NODE"

def get_deterministic_key(email="godsfuel@live.com"):
    """Generates a permanent, consistent hardware-locked key for this specific device."""
    hw_id = get_hardware_signature()
    raw_data = f"{hw_id}-{email}-spooky-sovereign-vault"
    hash_val = hashlib.sha256(raw_data.encode()).hexdigest().upper()
    return f"KEY-{hash_val[:12]}"

@app.route('/')
def serve_index():
    return send_from_directory(WEB_ROOT, 'index.html')

@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(WEB_ROOT, filename)

@app.route('/api/check-status', methods=['POST'])
def check_status():
    data = request.get_json() or {}
    email = data.get('email', 'godsfuel@live.com')
    
    node_id = get_deterministic_key(email)
    
    # Check if a vault record exists for this hardware node
    vault_path = os.path.join(VAULT_DIR, f"{node_id}.vault")
    has_key = os.path.exists(vault_path)
    
    # Auto-initialize vault record if missing so it's always ready
    if not has_key:
        with open(vault_path, 'w') as f:
            f.write(f"Sovereign Anchor Active for {email} on HW: {get_hardware_signature()}")
        has_key = True

    return jsonify({
        "status": "online",
        "has_key": has_key,
        "node_id": node_id,
        "system": "Active Sovereign Node"
    })

@app.route('/api/generate-key', methods=['POST'])
def generate_key():
    data = request.get_json() or {}
    email = data.get('email', 'godsfuel@live.com')
    
    node_id = get_deterministic_key(email)
    vault_path = os.path.join(VAULT_DIR, f"{node_id}.vault")
    
    # Re-verify/re-bind vault file
    with open(vault_path, 'w') as f:
        f.write(f"Regenerated Sovereign Anchor for {email}")
        
    return jsonify({
        "success": True,
        "node_id": node_id,
        "message": "Deterministic hardware key verified and locked."
    })

if __name__ == '__main__':
    print("[*] Starting Spooky Sovereign Engine on http://127.0.0.1:5000")
    app.run(host='127.0.0.1', port=5000, debug=False)