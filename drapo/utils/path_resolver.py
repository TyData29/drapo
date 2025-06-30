# # -*- coding: utf-8 -*-
"""
Module utilitaire pour résoudre les chemins de fichiers dans Drapo.
Il permet de convertir des chemins relatifs en chemins absolus basés sur le répertoire du script.
"""
import os



# === 1. Helpers for path resolution ===
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#print(f"Répertoire de base du script : {BASE_DIR}")


def resolve_path(path: str) -> str:
    """
    Si `path` est déjà absolu, le renvoyer tel quel.
    Sinon, le considérer relatif à BASE_DIR.
    """
    if os.path.isabs(path):
        return path
    return os.path.join(BASE_DIR, path)