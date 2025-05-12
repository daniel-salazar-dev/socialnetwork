"""
Handles logger management
"""

import os
from datetime import datetime
from loguru import logger

log_dir = os.path.dirname(os.path.abspath(__file__))
LOG_FILENAME = f"log_{datetime.now().strftime('%m-%d-%Y')}.log"
log_path = os.path.join(log_dir, LOG_FILENAME)

# Setup logger
logger.remove()
logger.add(
    log_path,
    level="INFO",
    format="{time:YYYY-MM-DD HH:mm:ss} - {level} - [{file}:{line}] - {message}",
)
