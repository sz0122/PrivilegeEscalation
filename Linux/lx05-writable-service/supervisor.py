#!/usr/bin/python3
# Supervisor for the monitor app.
# Runs as root every minute and re-executes the monitored app script.
import os
import subprocess
import time

LOG = "/var/log/monitor/supervisor.log"
APP = "/opt/monitor/app.py"


def log(msg):
    with open(LOG, "a") as f:
        f.write("[%s] %s\n" % (time.strftime("%F %T"), msg))


def main():
    log("checking monitor app")
    # Run the app with its own interpreter so ops can restart it safely
    subprocess.run(["/usr/bin/python3", APP], check=False)
    log("supervisor done")


if __name__ == "__main__":
    main()
