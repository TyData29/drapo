# -*- coding: utf-8 -*-
# scheduler.py
"""
Module pour programmer des tâches planifiées dans Drapo.
schedule_jobs est utilisé pour planifier des flux de travail basés sur la configuration fournie.
    Il utilise la bibliothèque `schedule` pour gérer les tâches planifiées.
    Paramètres:
        config (dict): Configuration des tâches à planifier, incluant les flux de travail et leurs horaires (fourni par ).
    Retourne:
        None
"""

import logging
import schedule
from drapo.orchestrer import run_flow



# === Scheduler setup ===
def schedule_jobs(config: dict):
    # build a map for lookup by name
    jobs_map = { job["name"]: job for job in config.get("jobs", []) }

    # only schedule the flow jobs
    for flow in (j for j in jobs_map.values() if j["type"] == "flow"):
        sched = flow["schedule"]
        tm    = flow["time"]
        steps = flow["steps"]
        if sched == "daily_at":
            schedule.every().day.at(tm).do(
                run_flow,
                steps=steps,
                jobs_map=jobs_map
            )
            logging.info("Flow '%s' planifié daily_at %s", flow["name"], tm)
        elif sched == "minute_at":
            schedule.every().minute.at(tm).do(
                run_flow,
                steps=steps,
                jobs_map=jobs_map
            )
            logging.info("Flow '%s' planifié minute_at %s", flow["name"], tm)
        elif sched == "hourly_at":
            schedule.every().hour.at(tm).do(
                run_flow,
                steps=steps,
                jobs_map=jobs_map
            )
            logging.info("Flow '%s' planifié hourly_at %s", flow["name"], tm)
        
        else:
            logging.error("Cron type non supporté: %s", sched)
