import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Render and other PaaS providers provide a PORT environment variable
    port = int(os.getenv("PORT", 8000))
    
    # If PORT is provided, we are likely in production and MUST bind to 0.0.0.0
    default_host = "0.0.0.0" if os.getenv("PORT") else "127.0.0.1"
    host = os.getenv("HOST", default_host)
    
    print(f"\n--- OLX GENIE PRODUCTION ENGINE ---")
    print(f"Status: STARTING")
    print(f"Binding: {host}:{port}")
    print(f"Mode: {'Production' if os.getenv('PORT') else 'Local'}")
    print(f"------------------------------------\n")
    
    uvicorn.run("src.api.app:app", host=host, port=port, reload=False)
