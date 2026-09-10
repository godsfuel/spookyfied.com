import os
import sys
import json
import platform
import hashlib
import subprocess

def initialize_stealth_node():
    system = platform.system()
    
    if system == "Windows":
        base_dir = os.path.join(os.environ.get("LOCALAPPDATA", "C:\\"), "Microsoft", "Windows", "SysCache")
        if not os.path.exists(base_dir):
            os.makedirs(base_dir, exist_ok=True)
            # Set Windows hidden/system attributes using attrib command
            subprocess.run(f'attrib +h +s "{base_dir}"', shell=True, stdout=subprocess.DEVNULL)
        config_path = os.path.join(base_dir, "sys_config_9f82.dat")
        
    elif system == "Darwin":
        base_dir = os.path.expanduser("~/Library/Application Support/.sys_cache")
        os.makedirs(base_dir, exist_ok=True)
        config_path = os.path.join(base_dir, "sys_manifest_v2.bin")
        
    else:
        base_dir = os.path.expanduser("~/.local/share/.sys_cache")
        os.makedirs(base_dir, exist_ok=True)
        config_path = os.path.join(base_dir, "sys_manifest_v2.bin")

    # Generate unique node hardware anchor
    machine_sig = platform.node() + platform.machine()
    node_id = "SYS-NODE-" + hashlib.sha256(machine_sig.encode()).hexdigest()[:16].upper()

    payload = {
        "node_id": node_id,
        "platform": system,
        "status": "SECURE_ACTIVE"
    }

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    if system == "Windows":
        subprocess.run(f'attrib +h +s "{config_path}"', shell=True, stdout=subprocess.DEVNULL)
    else:
        os.chmod(config_path, 0o600)

    print(f"[+] Spooky Sovereign Node Initialized: {node_id}")

if __name__ == "__main__":
    initialize_stealth_node()