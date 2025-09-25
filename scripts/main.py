from flask_server import app, post_heartbeat as heartbeat_fn
from web_driver import BunnyDriver
from threading import Thread
from hardware import background_process, set_BunnyDriver
import paramiko
import subprocess
from configparser import ConfigParser
from utils import *
import time
import os

logger = setup_logger("logs")
logger.info(f"Logger initialized inside ({os.path.splitext(os.path.basename(__file__))[0]}.py)")


home_dir = os.path.expanduser("~")
ssh_dir = os.path.join(home_dir, ".ssh")
key_path = os.path.join(ssh_dir, "bunny_server")
passphrase = "bunny_init"
_config = ConfigParser()
_config.read(os.path.join(os.path.dirname(__file__),"../config.ini"))
section = _config["Default"]
host = section["ip_server"]
username = "root"

# --------- Check for running app.py ---------
def count_app_py_processes():
    result = subprocess.run(
        ["ps", "aux"],
        stdout=subprocess.PIPE,
        text=True
    )
    lines = result.stdout.splitlines()
    count = 0
    for line in lines:
        if "python app.py" in line and "grep" not in line:
            count += 1
    return count

# --------- SSH bunny runner ---------
def run_remote_bunny():
    private_key = paramiko.RSAKey.from_private_key_file(key_path, password=passphrase)

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, pkey=private_key)

    channel = ssh.get_transport().open_session()
    channel.get_pty()
    channel.exec_command("bash -i -c 'bunny'")

    try:
        while True:
            if channel.exit_status_ready():
                break
            time.sleep(0.1)
    finally:
        logger.info("Closing channel and SSH connection...")
        channel.close()
        ssh.close()
    logger.info("SSH bunny started...")

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

# ---------- Main logic ----------

_BunnyDriver = BunnyDriver()
_BunnyDriver.init_driver()

# ---------- Main logic ----------
if count_app_py_processes() == 0:
    logger.info("No app.py processes found. Running SSH bunny command...")

    # Run SSH first
    ssh_thread = Thread(target=run_remote_bunny, daemon=True)
    ssh_thread.start()
else:
    logger.warning("app.py is already running. Skipping SSH bunny execution.")

# Start other background threads
flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

logger.info("Flask Server started...")

heartbeat_thread = Thread(target=heartbeat_fn, daemon=True)
heartbeat_thread.start()

logger.info("Server Connection thread started...")
set_BunnyDriver(_BunnyDriver)
serial_thread = Thread(target=background_process, daemon=True)
serial_thread.start()

logger.info("Background process thread started...")

time.sleep(20)
#await everything to connect

# Now run BunnyDriver in the main thread (GUI needs this)
try:
    _BunnyDriver.execute()  # This blocks, runs forever with Selenium GUI
except KeyboardInterrupt:
    print("Main program exiting...")
    _BunnyDriver.close_driver()
