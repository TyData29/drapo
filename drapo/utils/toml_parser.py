## -*- coding: utf-8 -*-
"""
Module pour charger la configuration d'orchestration depuis un fichier TOML.
"""
import logging
import toml
from drapo.utils import resolve_path    


def load_orchestration_config(fn: str) -> dict:
    path = resolve_path(fn)
    logging.info("Lecture de la config depuis %s", path)
    with open(path, "r", encoding="utf-8") as f:
        return toml.load(f)
