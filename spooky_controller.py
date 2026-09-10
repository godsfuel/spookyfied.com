import multiprocessing
import time
import sys
import os
import subprocess

# Define the production microservices for the Spooky Sovereign ecosystem
servers = [
    {
        "name": "Sovereign Portal Gateway",
        "file": "spooky_engine.py",
        "port": 5000
    },
    {
        "name": "Cave Master Vault Node",
        "file": "spooky_video.py",
        "port": 7000
    }
]

def run_server(script_name, server_name):
    print(f"[*] Starting {server_name} ({script_name})...")
    try:
        subprocess.run([sys.executable, script_name], check=True)
    except Exception as e:
        print(f"[!] {server_name} encountered an error: {e}")

if __name__ == "__main__":
    print("==================================================")
    print("   SPOOKY UNIFIED ECOSYSTEM MASTER CONTROLLER     ")
    print("   Domain Target: https://bounceairbags.com       ")
    print("==================================================")
    
    # Ensure local cave vault directory structure exists inside project folder
    vault_masters_dir = os.path.join(".", "cave_vault", "masters")
    os.makedirs(vault_masters_dir, exist_ok=True)
    print(f"[+] Local Vault Masters Directory Verified: {os.path.abspath(vault_masters_dir)}")

    processes = []
    
    for s in servers:
        if os.path.exists(s["file"]):
            p = multiprocessing.Process(target=run_server, args=(s["file"], s["name"]))
            processes.append(p)
            p.start()
            time.sleep(0.5) 
        else:
            print(f"[!] Warning: Required component '{s['file']}' not found in root directory.")
        
    print("\n[+] All core servers running in background threads.")
    print("[+] Press Ctrl+C at any time to gracefully shutdown all services.\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[!] Shutdown signal received. Stopping all Spooky servers...")
        for p in processes:
            p.terminate()
            p.join()
        print("[✓] All services safely terminated.")