# -*- coding: utf-8 -*-

import argparse
import os
import sys
import logging
import yaml
import toml
from logging.handlers import TimedRotatingFileHandler
import re



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

############################################### load_config ###############################################
"""
Module de chargement du fichier de configuration utilisé par Drapo
"""

def load_config(config_path: str) -> dict:
    """
    Charge le fichier YAML et résout les variables ${...}
    """
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    # Stocke les variables connues (project_root + paths)
    variables = {}
    variables["project_root"] = data["project_root"]

    # Commence par substituer project_root dans paths
    paths = {}
    for k, v in data["paths"].items():
        if isinstance(v, str):
            paths[k] = v.replace("${project_root}", data["project_root"])
    variables.update(paths)

    # Substitue dans flows
    flows = {}
    for k, v in data["flows"].items():
        resolved = v
        # Remplace toutes les occurrences ${...}
        matches = re.findall(r"\$\{(.+?)\}", v)
        for var in matches:
            resolved = resolved.replace("${" + var + "}", variables[var])
        flows[k] = resolved

    return {
        "project_root": data["project_root"],
        "paths": paths,
        "flows": flows
    }

# CONFIG = load_config("../config.yml")

############################################### Path resolver ###############################################
"""
Module utilitaire pour résoudre les chemins de fichiers dans Drapo.
Il permet d'exploiter les paths définis dans config.yml'
"""


def resolve_path(path: str, config: dict) -> str:
    """
    Résout un chemin relatif ou avec des variables à partir d'un dictionnaire de config.
    Exemple :
        resolve_path("${paths.dbt}", config)
    """
    # Si le chemin est absolu, retourne tel quel
    if os.path.isabs(path):
        return path

    # Remplace les variables ${...}
    variables = {"project_root": config.get("project_root", "")}
    variables.update(config.get("paths", {}))
    variables.update(config.get("flows", {}))

    resolved = path
    matches = re.findall(r"\$\{(.+?)\}", path)
    for var in matches:
        if var not in variables:
            raise ValueError(f"Variable '{var}' inconnue dans le chemin: {path}")
        resolved = resolved.replace("${" + var + "}", variables[var])

    # Normalise et absolutise
    return os.path.abspath(resolved)

############################################### TOML Parser ###############################################
"""
Module pour charger la configuration d'orchestration depuis un fichier TOML.
"""

def load_orchestration_config(CONFIG,fn: str) -> dict:
    path = resolve_path("${paths.drapoconfig}",CONFIG)
    logging.info("Lecture de la config depuis %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return toml.load(f)


########################################## Console logger ##########################################

def setup_logger(CONFIG):
    """
    Initialise le logger avec la config YAML passée en argument.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Under Windows switch console to UTF-8
    if os.name == "nt":
        os.system("chcp 65001 > nul")
        try:
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stderr.reconfigure(encoding="utf-8")
        except AttributeError:
            pass

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
    log_file = resolve_path("${paths.drapolog}", CONFIG)
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,
        encoding="utf-8",
    )
    file_handler.setFormatter(console_h)
    logger.addHandler(file_handler)

    return logger