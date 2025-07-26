import os
import logging
from datetime import datetime

# Setup log directory
LOG_DIR = os.path.join(os.getcwd(), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Log file name
LOG_FILE = f"{datetime.now().strftime('%Y-%m-%d')}.log"
LOG_FILE_PATH = os.path.join(LOG_DIR, LOG_FILE)

# Create logger instance
logger = logging.getLogger("networksecurity_logger")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOG_FILE_PATH)
file_handler.setLevel(logging.INFO)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Prevent adding handlers multiple times
if not logger.handlers:
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
