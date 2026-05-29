import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Robust port detection for various PaaS (Alwaysdata uses PORT or ALWAYSDATA_HTTP_PORT)
    port_env = os.getenv("ALWAYSDATA_HTTP_PORT") or os.getenv("PORT") or "8000"
    port = int(port_env.strip('"')) # Clean accidental quotes from environment
    host = "0.0.0.0"
    
    print(f"\n--- GENIE DEPLOYMENT SYSTEM ---")
    print(f"Status: ACTIVE")
    print(f"Binding: {host}:{port}")
    print(f"Detected Env: {'Alwaysdata' if os.getenv('ALWAYSDATA_HTTP_PORT') else 'Local/Other'}")
    print(f"-------------------------------\n")
    
    # '0.0.0.0' is mandatory for Alwaysdata to route traffic to the container
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)
