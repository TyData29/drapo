# -*- coding: utf-8 -*-
# runner_dbt.py
"""
Module pour exécuter des commandes dbt.
"""

import logging
from drapo.utils import resolve_path, stream_subprocess


def run_dbt_command(cmd: list[str], working_dir: str = None):
    """
    Exécute la commande dbt depuis working_dir (ou BASE_DIR si non fourni).
    """
    # s'il n'y a pas de working_dir ou s'il est vide, on utilise BASE_DIR
    wd = resolve_path(working_dir if working_dir else ".")
    logging.info("–> dbt working directory : %s", wd)
    exit_code = stream_subprocess(cmd, cwd=wd)
    if exit_code == 0:
        logging.info("✅ tâche dbt terminée.")
    else:
        logging.error("❌ tâche dbt a échoué (code %d).", exit_code)