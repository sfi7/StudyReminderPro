# ============================================================
# Study Reminder Pro - Logger Subsystem
# File: utils/logger.py
# ============================================================

import logging
import os
from datetime import datetime

# Path setup
APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOGS_DIR = os.path.join(APP_DIR, "logs")

def setup_logger():
    """Initializes the centralized application logger."""
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, "app.log")

    logger = logging.getLogger("StudyReminderPro")
    
    # Only configure if it doesn't already have handlers
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)

        # Formatter
        formatter = logging.Formatter(
            fmt='[%(asctime)s] [%(levelname)s] [%(module)s:%(lineno)d] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # File Handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    return logger

# Expose a global logger instance
log = setup_logger()
