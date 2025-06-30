import os
import logging
import subprocess


# stream_subprocess est utilisé pour exécuter des jobs en streaming (avec des logs en temps réel),
def stream_subprocess(cmd: list[str], cwd: str | None = None, args : list | None = None) -> int:
    """
    Exécute `cmd` et stream stdout+stderr ligne par ligne vers le logger,
    en mode texte, ligne-buffered.
    """
    
    logging.info("[>>>RUN>>>] : %s", " ".join(cmd))
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    # text=True pour recevoir str, bufsize=1 pour line-buffered
    proc = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        cwd=cwd,
        env=env,
        text=True,
        bufsize=1
    )

    # Itérer directement sur proc.stdout pour chaque ligne
    assert proc.stdout
    for line in proc.stdout:
        logging.info(line.rstrip())

    if args.dry_run:
        logging.info("[DRY RUN] Commande: %s", " ".join(cmd))
        return 0

    code = proc.wait()
    return code

