import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Alwaysdata assigns a port dynamically
    port = int(os.getenv("ALWAYSDATA_HTTP_PORT", 8000))
    # '0.0.0.0' is required for external access through the proxy
    uvicorn.run("src.api.app:app", host="0.0.0.0", port=port, reload=False)
