import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Render and other PaaS providers provide a PORT environment variable
    # We default to 8000 for local development
    port = int(os.getenv("PORT", 8000))
    
    # Binding to 0.0.0.0 is mandatory for production environments
    # but we can use 127.0.0.1 for local dev if preferred.
    # On Render, 0.0.0.0 is required.
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"\n--- OLX GENIE PRODUCTION ENGINE ---")
    print(f"Binding: {host}:{port}")
    print(f"------------------------------------\n")
    
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)
