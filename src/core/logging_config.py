import logging
import json
from datetime import datetime

class JsonFormatter(logging.Formatter):
    """
    Standard JSON formatter for structured logging.
    Transforms log records into machine-readable JSON objects.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_object = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "funcName": record.funcName,
        }
        
        # Include exception info if present
        if record.exc_info:
            log_object["exception"] = self.formatException(record.exc_info)
        
        # Include extra attributes if provided (via 'extra' kwarg in logger calls)
        if hasattr(record, "extra"):
            log_object.update(record.extra)
            
        return json.dumps(log_object)

def setup_json_logging():
    """Configures the root logger to use JSON formatting."""
    root_logger = logging.getLogger()
    
    # Remove existing handlers to avoid double logging
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler()
    handler.setFormatter(JsonFormatter())
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)
    
    # Silence third-party noise
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiogram").setLevel(logging.INFO)

# Global logger instance
logger = logging.getLogger("olxbot")
