# -*- coding: utf-8 -*-
# runner_git.py
"""
Module pour exécuter des commandes git.
"""

import os
import logging
from utils.path_resolver import resolve_path


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