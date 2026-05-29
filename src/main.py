import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Standard local/generic configuration
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    
    print(f"\n--- OLX GENIE STARTING ---")
    print(f"Binding: {host}:{port}")
    print(f"--------------------------\n")
    
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)
