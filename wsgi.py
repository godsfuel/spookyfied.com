from app import app
from waitress import serve

if __name__ == "__main__":
    print("==================================================")
    print("  SPOOKY SOVEREIGN ENTERPRISE SERVER INITIALIZED  ")
    print("  Mode: Production WSGI (Waitress)                 ")
    print("  Engine: spooky_engine.py ONLINE & BOUND          ")
    print("  Listening on port 5000...                        ")
    print("==================================================")
    
    serve(app, host="0.0.0.0", port=5000, threads=8)