# # -*- coding: utf-8 -*-
# # orchestrer.py
"""
Module pour orchestrer l'exécution des workflows de jobs Python, dbt et git.
    
    run_flow est la fonction principale qui permet orchestrer les jobs définis dans la configuration.

"""

import os
import sys
import time
import logging
import argparse
import subprocess

from utils import resolve_path
from runners import *


def run_flow(python_distrib : str, steps: list[str], jobs_map: dict[str, dict], args: argparse.Namespace):
    """
    Orchestrate a sequence of jobs:
     - first step must be a connection check
     - then python and dbt steps
    """
    # 1) connection check
    conn_job = jobs_map.get(steps[0])
    if conn_job and conn_job["type"] == "connection":
        ip    = conn_job["host"] if os.name != "nt" else "10.0.0.45"
        port  = conn_job["port"]
        retry = conn_job.get("retry_interval_min", 10)
        while True:
            logging.info("Vérification de %s:%d …", ip, port)
            if is_server_reachable(ip, port):
                logging.info("Connexion OK, on poursuit le flow.")
                break
            logging.info("Attente %d min avant nouvelle tentative.", retry)
            time.sleep(retry * 60)
    else:
        logging.error("Metajob de connexion manquant ou incorrect.")

    # 2) subsequent steps
    for step_name in steps[1:]:
        job = jobs_map.get(step_name)
        logging.info(">>>>>>>>>>>>>>>>> JOB : %s >>>>>>>>>>>>>>>>>", step_name)
        if not job:
            logging.error("Job inconnu dans le flow: %s", step_name)
            continue

        if job["type"] == "python":
            interp = python_distrib if python_distrib else job.get("interpreter", sys.executable)
            script = resolve_path(job["script_path"])
            args.python_args = args.python_args if hasattr(args, "python_args") else ""
            logging.info("Exécution du script Python %s avec interpréteur %s", script, interp)
            run_python_script(
                python_interpreter=interp,
                script_path=script,
                args=args.python_args if hasattr(args, "python_args") else ""
            )
        elif job["type"] == "dbt":
            run_dbt_command(
                cmd = job["cmd"] + args.dbt_args.split() if "dbt_args" in args else [],
                working_dir=job.get("working_dir")
            )
        elif job["type"] == "git":
            update_git_repo(
                repo_dir=job["repo_dir"],
                branch=job["branch"]
            )
        elif job["type"] == "dependencies":
            install_dependencies()
        else:
            logging.error("Type de job non géré: %s", job["type"])

        logging.info("<<<<<<<<<<<<<<<<< JOB %s terminé <<<<<<<<<<<<<<<<<", job["name"])