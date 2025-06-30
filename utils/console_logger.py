# # -*- coding: utf-8 -*-
# """
# Module de gestion des logs de Drapo
# """
import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from drapo.utils import resolve_path


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),  # Output to console
        logging.FileHandler("orchestrator.log")  # Output to file
    ]
)

# === 0. Under Windows switch console to UTF-8 ===
if os.name == "nt":
    os.system("chcp 65001 > nul")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except AttributeError:
        pass




# === 2. Logger setup ===
logger = logging.getLogger()  
logger.setLevel(logging.INFO)

format_str = "%(asctime)s [%(levelname)s] %(message)s"
date_fmt   = "%Y-%m-%d %H:%M:%S"

# Console handler
console_h = logging.StreamHandler()
console_formatter = logging.Formatter(format_str, datefmt=date_fmt)
console_h.setFormatter(console_formatter)
logger.addHandler(console_h)

# File handler (rotates daily, keeps 30 days)
log_file = resolve_path("orchestration.log")
file_handler = TimedRotatingFileHandler(
    filename=log_file,
    when="midnight",
    interval=1,
    backupCount=30,
    encoding="utf-8",
)
file_handler.setFormatter(console_h)
logger.addHandler(file_handler)

