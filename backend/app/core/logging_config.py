import logging
import sys
from contextvars import ContextVar
from typing import Optional

# Context variable to hold the request ID
request_id_var: ContextVar[Optional[str]] = ContextVar("request_id", default=None)

class RequestIdFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        req_id = request_id_var.get()
        if req_id:
            record.req_id_prefix = f"[request_id={req_id}] "
        else:
            record.req_id_prefix = ""
        return super().format(record)

def setup_logging():
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    formatter = RequestIdFormatter(
        "%(asctime)s | %(levelname)s | %(req_id_prefix)s%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    root_logger.addHandler(console_handler)
    root_logger.setLevel(logging.INFO)
    
    # Silence noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
