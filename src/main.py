import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Alwaysdata assigns a port dynamically
    port = int(os.getenv("ALWAYSDATA_HTTP_PORT", 8000))
    host = "0.0.0.0"
    
    print(f"--- DEPLOYMENT DIAGNOSTICS ---")
    print(f"Target Host: {host}")
    print(f"Target Port: {port}")
    print(f"ALWAYSDATA_HTTP_PORT: {os.getenv('ALWAYSDATA_HTTP_PORT')}")
    print(f"------------------------------")
    
    # '0.0.0.0' is required for external access through the proxy
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)
