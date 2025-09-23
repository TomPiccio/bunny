import os
import time
import signal
import sys

RPiActive = False
_shouldIShutDown = False
power_state = True

from utils import setup_logger
logger = setup_logger()

def shutDownProcess():
    global power_state
    # Play shut down audio
    if RPiActive:
        os.system("sudo shutdown -h +1")
    logger.critical("Shutting Down!")
    power_state = False
    if _shouldIShutDown:
        time.sleep(30)
        pid = os.getpid()
        os.kill(pid, signal.SIGINT)  # Send SIGINT (equivalent to Ctrl+C)
        sys.exit()

def get_power_state():
    return power_state

def get_RPiActive():
    return RPiActive

