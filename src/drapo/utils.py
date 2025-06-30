# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import toml


################################################# CLI Parser #################################################
def parse_args():
    """
    Parse command line arguments for the DRAPO orchestrator.
    """ 
    # Create the argument parser
    parser = argparse.ArgumentParser(description="DRAPO Orchestrator")

    parser.add_argument( # Argument pour choisir l'environnement d'exécution
        "--env",
        choices=["prod", "test", "local"],
        default="prod",
        help="Choose the execution environment: prod, test, or local (default: prod)"
    )

    parser.add_argument( # Argument pour forcer l'exécution immédiate des flows
        "--enforce",
        action="store_true",
        help="Bypass scheduler and run all flows immediately, then exit"
    )

    parser.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    parser.add_argument("--dry-run", action="store_true") # Argument pour un mode de test sans exécution réelle
    #parser.add_argument("--dbt-args", default="") # Possibilité de passer des arguments à dbt
    #parser.add_argument("--git-args", default="") # Possibilité de passer des arguments à git
    #parser.add_argument("--python-interpreter", default=sys.executable) # Interpréteur Python à utiliser
    #parser.add_argument("--python-script", default="") # Chemin du script Python à exécuter
    #parser.add_argument("--python-args", default="") # Arguments à passer au script Python

    return parser.parse_args()

############################################### Path resolver ###############################################
"""
Module utilitaire pour résoudre les chemins de fichiers dans Drapo.
Il permet de convertir des chemins relatifs en chemins absolus basés sur le répertoire du script.
"""




# === 1. Helpers for path resolution ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#print(f"Répertoire de base du script : {BASE_DIR}")
# Ensure the base directory is in the system path for module imports
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)


def resolve_path(path: str) -> str:
    """
    Si `path` est déjà absolu, le renvoyer tel quel.
    Sinon, le considérer relatif à BASE_DIR.
    """
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)

############################################### TOML Parser ###############################################
"""
Module pour charger la configuration d'orchestration depuis un fichier TOML.
"""

def load_orchestration_config(fn: str) -> dict:
    path = resolve_path(fn)
    logging.info("Lecture de la config depuis %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return toml.load(f)


########################################## Console logger ##########################################



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

