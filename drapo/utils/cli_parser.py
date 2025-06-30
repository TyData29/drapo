#     
import argparse

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