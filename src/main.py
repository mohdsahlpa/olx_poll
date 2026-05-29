import uvicorn
import os
import sys

# Ensure src is in python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    # Disable reload=True to prevent TelegramConflictError during development
    uvicorn.run("src.api.app:app", host="127.0.0.1", port=8000, reload=False)
