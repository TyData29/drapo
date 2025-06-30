
# -*- coding: utf-8 -*-
# runner_python.py
"""
Module pour exécuter des scripts python.
"""

import os
import sys
import logging
from drapo.utils import resolve_path, stream_subprocess

def run_python_script(python_interpreter: str, script_path: str, args: str = ""):
    """
    Exécute un script Python via l'interpréteur donné,
    avec fallback sur sys.executable si le chemin n'est pas valide.
    """
    # 1) Résolution et vérification de l'interpréteur
    interp = resolve_path(python_interpreter)
    if not os.path.isfile(interp):
        logging.warning(
            "Interpreter introuvable (%s), fallback vers %s",
            interp, sys.executable
        )
        interp = sys.executable

    # 2) Résolution et vérification du script
    script = resolve_path(script_path)
    if not script.endswith(".py"):
        logging.error("Le script doit être un fichier Python (.py) : %s", script)
        return
    if not os.path.isfile(script):
        logging.error("Script Python introuvable : %s", script)
        return

    # 3) Exécution en streaming avec passage des arguments
    if args:
        cmd = [interp, script] + args.split()
    else:
        cmd = [interp, script]
    exit_code = stream_subprocess(
        cmd,
        cwd=os.path.dirname(script)
    )

    # 4) Log du résultat
    if exit_code == 0:
        logging.info("✅ Script Python exécuté avec succès.")
    else:
        logging.error("❌ Échec du script Python (code %d).", exit_code)