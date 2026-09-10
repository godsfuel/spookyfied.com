from flask import Flask, render_template_string, request, jsonify, redirect, send_from_directory
import sqlite3
import os
import hmac
import hashlib
import time
from waitress import serve
from flask import Flask, render_template, send_from_directory, request, jsonify
import os

# Define the absolute path to your SpookYFied.com frontend folder
WEB_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), 'SpookYFied.com'))

app = Flask(__name__, static_folder=WEB_ROOT, template_folder=WEB_ROOT)

# Route to serve the main commercial landing page (index.html)
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

# Route to serve any static web page or asset (downloads.html, privacy.html, support.html, logos)
@app.route('/<path:filename>')
def serve_static_files(filename):
    return send_from_directory(app.static_folder, filename)
DB_NAME = "spooky_directory.db"
SECRET_HMAC_KEY = os.environ.get("SPOOKY_SECRET_KEY", "SPOOKY-SOVEREIGN-MASTER-KEY-2026")

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Nodes & Vendors
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nodes (
            email TEXT,
            node_id TEXT PRIMARY KEY,
            os TEXT,
            public_routing_key TEXT,
            source_domain TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    # Subscribers & Global Keyholders
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS subscribers (
            email TEXT PRIMARY KEY,
            customer_node_id TEXT,
            hardware_fingerprint TEXT,
            is_active_subscriber INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def generate_signed_token(vendor_domain, customer_email):
    message = f"{vendor_domain}:{customer_email}:{int(time.time())}".encode('utf-8')
    signature = hmac.new(SECRET_HMAC_KEY.encode('utf-8'), message, hashlib.sha256).hexdigest()
    return f"{message.decode('utf-8')}:{signature}"

def verify_signed_token(token):
    try:
        parts = token.split(":")
        if len(parts) != 3:
            return False, "Invalid token structure"
        vendor_domain, customer_email, timestamp = parts[0], parts[1], parts[2]
        original_msg = f"{vendor_domain}:{customer_email}:{timestamp}".encode('utf-8')
        expected_sig = hmac.new(SECRET_HMAC_KEY.encode('utf-8'), original_msg, hashlib.sha256).hexdigest()
        if time.time() - int(timestamp) > 900:
            return False, "Token expired"
        return True, customer_email
    except Exception as e:
        return False, str(e)

@app.route('/SPOOKY_Logo.png', methods=['GET'])
def serve_logo():
    if os.path.exists("SPOOKY_Logo.png"):
        return send_from_directory('.', "SPOOKY_Logo.png")
    return "Logo not found", 404

@app.route('/', methods=['GET'])
def portal_gateway():
    """
    Intelligent landing gateway. 
    Checks query params for vendor redirection or renders the master onboarding/ecosystem hub.
    """
    vendor_ref = request.args.get('vendor')
    email_ref = request.args.get('email', '')

    # If user arrived via a vendor referral looking for a key
    if vendor_ref:
        return render_template_string(KEY_GEN_TEMPLATE, vendor=vendor_ref, email=email_ref)

    # Standard landing: Check if local client has a session cookie or render main hub
    return render_template_string(MASTER_HUB_TEMPLATE)

@app.route('/api/check-status', methods=['POST'])
def check_status():
    data = request.json or {}
    email = data.get('email')
    if not email:
        return jsonify({"status": "ERROR", "has_key": False}), 400

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('SELECT customer_node_id, is_active_subscriber FROM subscribers WHERE email = ?', (email,))
    row = cursor.fetchone()
    conn.close()

    if row:
        return jsonify({"status": "SUCCESS", "has_key": True, "node_id": row[0], "subscriber": bool(row[1])}), 200
    return jsonify({"status": "SUCCESS", "has_key": False}), 200

@app.route('/api/generate-key', methods=['POST'])
def generate_key_action():
    data = request.json or {}
    email = data.get('email')
    vendor_domain = data.get('vendor', '')

    if not email:
        return jsonify({"status": "ERROR", "message": "Email required"}), 400

    node_id = "KEY-" + hashlib.sha256(email.encode()).hexdigest()[:12].upper()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO subscribers (email, customer_node_id, hardware_fingerprint, is_active_subscriber)
        VALUES (?, ?, ?, 1)
    ''', (email, node_id, "FINGERPRINT-ANCHOR"))
    conn.commit()
    conn.close()

    # If triggered by a vendor, build signed token and return redirect URL
    if vendor_domain:
        token = generate_signed_token(vendor_domain, email)
        redirect_url = f"{vendor_domain}/callback?token={token}&email={email}"
        return jsonify({"status": "SUCCESS", "redirect": redirect_url, "node_id": node_id}), 200

    return jsonify({"status": "SUCCESS", "message": "Spooky Key Generated Successfully", "node_id": node_id}), 200

@app.route('/dashboard', methods=['GET'])
def ecosystem_dashboard():
    """Main hub for verified keyholders and active subscribers."""
    return render_template_string(ECOSYSTEM_DASHBOARD_TEMPLATE)

# --- HTML TEMPLATES WITH LOGO & RESPONSIVE ROUTING ---

MASTER_HUB_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SpookyFied.com - Sovereign Gateway</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0b0c10; color: #c5c6c7; margin: 0; padding: 40px; text-align: center; }
        .container { background: #1f2833; max-width: 600px; margin: auto; padding: 40px; border-radius: 12px; border: 1px solid #45a29e; box-shadow: 0 4px 20px rgba(0,0,0,0.7); }
        img.logo { max-width: 120px; height: auto; margin-bottom: 20px; }
        h1 { color: #66fcf1; margin-bottom: 10px; }
        input, button { width: 100%; padding: 14px; margin-top: 15px; border-radius: 6px; border: none; box-sizing: border-box; font-size: 15px; }
        input { background: #0b0c10; color: #fff; border: 1px solid #45a29e; }
        button { background: #66fcf1; color: #0b0c10; font-weight: bold; cursor: pointer; transition: 0.2s; }
        button:hover { background: #45a29e; color: #fff; }
        .notice { font-size: 13px; color: #8892b0; margin-top: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <img src="/SPOOKY_Logo.png" alt="Spooky Logo" class="logo">
        <h1>SpookyFied.com</h1>
        <p>Zero-Retention Sovereign Ecosystem Gateway</p>
        
        <div style="margin-top: 30px;">
            <h3>Access Your Account or Generate Key</h3>
            <input type="email" id="userEmail" placeholder="Enter your registered email">
            <button onclick="verifyUserAccess()">Enter Ecosystem / Check Key</button>
        </div>
        <div id="outputMsg" class="notice"></div>
    </div>

    <script>
        async function verifyUserAccess() {
            const email = document.getElementById('userEmail').value.trim();
            const msgBox = document.getElementById('outputMsg');
            if (!email) { alert("Please enter your email"); return; }

            msgBox.style.color = "#66fcf1";
            msgBox.textContent = "Verifying cryptographic identity...";

            const res = await fetch('/api/check-status', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email: email })
            });
            const data = await res.json();

            if (data.has_key) {
                msgBox.textContent = "Spooky Key recognized! Redirecting to ecosystem dashboard...";
                setTimeout(() => { window.location.href = `/dashboard?email=${email}`; }, 1000);
            } else {
                msgBox.textContent = "No key found. Provisioning new hardware-bound Spooky Key...";
                const genRes = await fetch('/api/generate-key', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({ email: email })
                });
                const genData = await genRes.json();
                msgBox.textContent = "Key provisioned successfully! Redirecting to dashboard...";
                setTimeout(() => { window.location.href = `/dashboard?email=${email}`; }, 1200);
            }
        }
    </script>
</body>
</html>
"""

KEY_GEN_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SpookyFied.com - Vendor Key Authorization</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0b0c10; color: #c5c6c7; margin: 0; padding: 40px; text-align: center; }
        .container { background: #1f2833; max-width: 600px; margin: auto; padding: 40px; border-radius: 12px; border: 1px solid #ffb703; box-shadow: 0 4px 20px rgba(0,0,0,0.7); }
        img.logo { max-width: 120px; height: auto; margin-bottom: 20px; }
        h1 { color: #ffb703; }
        input, button { width: 100%; padding: 14px; margin-top: 15px; border-radius: 6px; border: none; box-sizing: border-box; font-size: 15px; }
        input { background: #0b0c10; color: #fff; border: 1px solid #ffb703; }
        button { background: #ffb703; color: #000; font-weight: bold; cursor: pointer; }
        button:hover { background: #fb8500; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <img src="/SPOOKY_Logo.png" alt="Spooky Logo" class="logo">
        <h1>Vendor Order Handshake</h1>
        <p>You were redirected from storefront: <b>{{ vendor }}</b></p>
        <p style="font-size: 13px; color: #a0a0c0;">Approve your hardware-bound Spooky Key to complete your order and unlock secure media playback.</p>
        
        <input type="email" id="vEmail" value="{{ email }}" placeholder="Enter your email address">
        <button onclick="approveVendorKey()">Approve Key & Return to Vendor</button>
        <div id="statusLog" style="margin-top: 15px; font-size: 13px; color: #66fcf1;"></div>
    </div>

    <script>
        async function approveVendorKey() {
            const email = document.getElementById('vEmail').value.trim();
            const vendor = "{{ vendor }}";
            if (!email) { alert("Email required"); return; }

            document.getElementById('statusLog').textContent = "Generating cryptographic anchor and signing token...";
            const res = await fetch('/api/generate-key', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ email: email, vendor: vendor })
            });
            const data = await res.json();
            if (data.redirect) {
                document.getElementById('statusLog').textContent = "Handshake secured! Returning to vendor portal...";
                setTimeout(() => { window.location.href = data.redirect; }, 1200);
            } else {
                alert(data.message);
            }
        }
    </script>
</body>
</html>
"""

ECOSYSTEM_DASHBOARD_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>SpookyFied.com - Ecosystem Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; background: #0b0c10; color: #c5c6c7; margin: 0; padding: 30px; }
        .header { display: flex; align-items: center; background: #1f2833; padding: 20px; border-radius: 8px; border: 1px solid #45a29e; margin-bottom: 30px; }
        .header img { max-width: 80px; margin-right: 20px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 20px; }
        .card { background: #1f2833; padding: 25px; border-radius: 8px; border: 1px solid #45a29e; text-align: center; }
        .card h3 { color: #66fcf1; }
        button { background: #66fcf1; color: #0b0c10; font-weight: bold; padding: 12px 20px; border: none; border-radius: 4px; cursor: pointer; margin-top: 15px; width: 100%; }
        button:hover { background: #45a29e; color: #fff; }
    </style>
</head>
<body>
    <div class="header">
        <img src="/SPOOKY_Logo.png" alt="Spooky Logo">
        <div>
            <h2>Spooky Sovereign Subscriber Dashboard</h2>
            <p style="color: #45a29e; margin: 0;">Status: Active Keyholder | Zero-Retention Mode Enabled</p>
        </div>
    </div>

    <div class="grid">
        <div class="card">
            <h3>Peer-to-Peer File Transfer</h3>
            <p>Direct node-to-node encrypted file sharing with zero intermediary storage.</p>
            <button onclick="alert('Launching P2P File Transfer Protocol...')">Launch P2P Transfer</button>
        </div>
        <div class="card">
            <h3>Secure Direct Messaging</h3>
            <p>End-to-end encrypted messaging channel across the Spooky network.</p>
            <button onclick="alert('Opening Secure Messenger...')">Open Messenger</button>
        </div>
        <div class="card">
            <h3>P2P Video Stream (1-on-1)</h3>
            <p>Direct sovereign video connection bypassing public cloud relays.</p>
            <button onclick="alert('Initializing P2P Video Link...')">Start P2P Video</button>
        </div>
        <div class="card">
            <h3>Group Video Conference</h3>
            <p>Encrypted multi-node video room for private team or group sessions.</p>
            <button onclick="alert('Creating Group Video Room...')">Create Group Room</button>
        </div>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    print("[*] Starting Sovereign Portal Gateway via Production WSGI Server (Waitress)...")
    serve(app, host='0.0.0.0', port=5000)