## -*- coding: utf-8 -*-
# runner_testreachable.py
"""
Module pour tester la connectivité d'un serveur via TCP.
"""
import socket
import logging

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