import os
import argparse
import logging
import sys
import time
import schedule
from drapo.utils import *
from drapo.orchestrer import run_flow
from drapo.scheduler import schedule_jobs



### ============================== Main function ============================== ###
def main():
    
    # 1. Parse command-line arguments
    args = parse_args()

    # 2. Log startup
    logging.info("---> Starting orchestrator (enforce=%s)...", args.enforce)
    logging.info(f"Python interpreter in use: {sys.executable}")

    THIS_DIR = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )
    CONFIG_PATH = os.path.join(THIS_DIR, "config.yml")

    print(f"Using config path: {CONFIG_PATH}")

    CONFIG = load_config(CONFIG_PATH)

    logger = setup_logger(CONFIG)

    # Accès aux fichiers de flows
    FLOWS = CONFIG["flows"]

    # 3. Choose config file
    config_file = FLOWS[f"{args.env}"]

    logging.info("Loading configuration %s", config_file)
    try:
        flowconfig = load_orchestration_config(fn=config_file)
    except FileNotFoundError:
        logging.error("Config file %s not found.", config_file)
        sys.exit(1)
    logging.info("Configuration loaded successfully.")

    # 4. Build jobs_map
    jobs_map = { job["name"]: job for job in flowconfig.get("jobs", []) }

    # 5. If enforce, immediately run each flow and exit
    if args.enforce:
        logging.info("Enforce mode: running flows immediately (no scheduling).")
        # find all 'flow' jobs
        for flow in (j for j in jobs_map.values() if j["type"] == "flow"):
            logging.info("→ Enforce-running flow '%s'", flow["name"])
            try:
                run_flow(CONFIG, python_distrib=sys.executable, steps=flow["steps"], jobs_map=jobs_map)
            except Exception as e:
                logging.error("Error in flow %s: %s", flow["name"], e)
        logging.info("All flows executed in enforce mode. Exiting.")
        sys.exit(0)

    # 6. Otherwise schedule normally
    try:
        schedule_jobs(flowconfig)
    except Exception as e:
        logging.error("Error scheduling jobs: %s", e)
        sys.exit(1)

    logging.info("Job scheduling complete. Waiting for executions...")
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logging.info("Scheduler interrupted manually.")


if __name__ == "__main__":
    main()
