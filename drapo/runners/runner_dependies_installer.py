# -*- coding: utf-8 -*-
# runner_dependencies_installer.py
"""
Module pour vérifier et installer les dépendances du projet parent orchestré par Drapo.
"""

# Runs install.bat or install.sh to install dependencies for the parent project orchestred by Drapo.
# If the script is run in a virtual environment, it will install the dependencies in the virtual environment.
# If the script is run in a Docker container, it will install the dependencies in the container.
# If the script is run in a GitHub Actions workflow, it will install the dependencies in the workflow.
import os
import sys
import subprocess   
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
if __name__ == "__main__":
    install_dependencies()
    print("Runner dependencies installer executed successfully.")
# This script is intended to be run as a standalone script to install dependencies for the Drapo project.
# It can be used in various environments such as local development, Docker containers, or CI/CD pipelines.
# The script will automatically detect the environment and install the dependencies accordingly.
# It is not intended to be imported as a module in other scripts.
# The script will exit with an error message if the install script is not found or if there is an error running the install script.
# It will print a success message if the dependencies are installed successfully.
