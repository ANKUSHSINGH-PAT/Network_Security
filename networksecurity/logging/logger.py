import os
import logging
from datetime import datetime


LOG_FILE=f"{datetime.now().strftime('%Y-%m-%d')}.log"
LOG_FILE_PATH = os.path.join(os.getcwd(), 'logs', LOG_FILE)

os.makedirs(os.path.dirname(LOG_FILE_PATH), exist_ok=True)

logging.basicConfig(
    filename=LOG_FILE_PATH,
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

