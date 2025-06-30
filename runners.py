# -*- coding: utf-8 -*-
import os
import sys
import subprocess 
import socket
import logging
from drapo.utils import resolve_path
from drapo.common import stream_subprocess


################################################# Runner dbt #################################################
"""
Module pour exécuter des commandes dbt.
"""
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

################################################# Runner dependencies_installer #################################################
"""
Module pour vérifier et installer les dépendances du projet parent orchestré par Drapo.
"""
# Runs install.bat or install.sh to install dependencies for the parent project orchestred by Drapo.
# If the script is run in a virtual environment, it will install the dependencies in the virtual environment.
# If the script is run in a Docker container, it will install the dependencies in the container.
# If the script is run in a GitHub Actions workflow, it will install the dependencies in the workflow.
def install_dependencies():
    """
    Installs dependencies for the parent project orchestrated by Drapo.
    """
    # Determine the script name and path
    script_name = os.path.basename(__file__)
    script_path = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_path)

    # Determine the install script based on the operating system
    if sys.platform.startswith('win'):
        install_script = os.path.join(parent_dir, 'install.bat')
    else:
        install_script = os.path.join(parent_dir, 'install.sh')
    # Check if the install script exists
    if not os.path.exists(install_script):
        print(f"Install script {install_script} not found.")
        sys.exit(1)
    # Run the install script
    try:
        print(f"Running install script: {install_script}")
        subprocess.run([install_script], check=True, shell=True)
        print("Dependencies installed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error running install script: {e}")
        sys.exit(1)

################################################# Runner git #################################################
"""
Module pour exécuter des commandes git.
"""
def update_git_repo(repo_dir: str, branch: str):    
    """
    Update the git repository in repo_dir to the specified branch.
    On Windows, this function does not update the repository and returns immediately.
    On other platforms, it performs 'git fetch' and 'git reset --hard origin/branch'.
    Args : 
        repo_dir (str): Path to the git repository directory.
        branch (str): The branch to update to.
    Returns:
        None if on Windows, otherwise the exit code of the git command.
    Raises:
        RuntimeError: If the git command fails.
    """
    rd = resolve_path(repo_dir)
    logging.info("→ Updating Git repo in %s to branch %s", rd, branch)
    cmds = [
        ["git", "fetch", "origin", branch],
        # Optionally add more git commands here if needed
    ]
    # Option B: just git pull 
    # cmds = [["git", "pull", "origin", branch]]
    if os.name == "nt":
        logging.info("On Windows: skipping git pull in development mode.")
        return None  # On Windows in development mode, do not fetch repo content!
    else:
        for cmd in cmds:
            code = stream_subprocess(cmd, cwd=rd)
            if code != 0:
                logging.error("Git command %s failed with code %d", cmd, code)
                # Raising RuntimeError will stop the flow execution for this job.
                raise RuntimeError("Git update failed")
        logging.info("✅ Git repo is now up-to-date on %s", branch)
    logging.info("✅ Git repo is now up-to-date on %s", branch)

################################################# Runner python #################################################
"""
Module pour exécuter des scripts python.
"""
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

################################################# Runner test reachable #################################################
"""
Module pour tester la connectivité d'un serveur via TCP.
"""
def is_server_reachable(ip: str, port: int, timeout: float = 5.0) -> bool:
    """
    Teste une connexion TCP; retourne True en cas de succès, False sinon.
    """
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return True
    except Exception as e:
        logging.warning("Serveur %s:%d non joignable : %s", ip, port, e)
        return False