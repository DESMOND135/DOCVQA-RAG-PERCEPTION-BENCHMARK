import logging
import os
import sys
from datetime import datetime

# FORCE UNBUFFERED STDOUT
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout.reconfigure(line_buffering=True)

# Define Log directory
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Define Log file format
LOG_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Function to get the logger
def get_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Clear existing handlers to avoid duplication during multiple imports
    if logger.hasHandlers():
        logger.handlers.clear()
        
    # File Handler
    try:
        fh = logging.FileHandler(LOG_FILE_PATH, encoding='utf-8')
        fh.setFormatter(logging.Formatter("[ %(asctime)s ] [%(name)s] [%(levelname)s] - %(message)s"))
        logger.addHandler(fh)
    except Exception:
        pass
        
    # Stream Handler (Console/Stdout) - Primary for user visibility
    class FlushingStreamHandler(logging.StreamHandler):
        def emit(self, record):
            super().emit(record)
            self.flush()

    ch = FlushingStreamHandler(sys.stdout)
    ch.setFormatter(logging.Formatter("[%(asctime)s] [%(levelname)s] [%(name)s] - %(message)s", datefmt="%H:%M:%S"))
    logger.addHandler(ch)
    
    # Prevent propagation
    logger.propagate = False
        
    return logger
