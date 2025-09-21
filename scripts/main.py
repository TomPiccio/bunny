from flask_server import app, post_heartbeat as heartbeat_fn
from web_driver import BunnyDriver
from threading import Thread
from hardware import background_process

import subprocess
from configparser import ConfigParser
import time

def run_bunny():
    # Read config.ini for ip_server
    config = ConfigParser()
    config.read("config.ini")

    try:
        ip_server = config.get("DEFAULT", "ip_server")
    except Exception as e:
        print(f"Could not read ip_server: {e}")
        return

    # Run bunny alias on server
    try:
        print(f"Running 'bunny' alias on {ip_server}...")
        subprocess.run([
            "ssh", f"pi@{ip_server}", "bash -lc 'bunny'"
        ])
    except Exception as e:
        print(f"Error running bunny: {e}")

# Create a thread
bunny_thread = Thread(target=run_bunny, daemon=True)
bunny_thread.start()

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True)

flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

heartbeat_thread = Thread(target=heartbeat_fn, daemon=True)
heartbeat_thread.start()

serial_thread = Thread(target=background_process, daemon=True)
serial_thread.start()

_BunnyDriver = BunnyDriver()
_BunnyDriver.execute()

while True:
    print("Main program still alive...")
    time.sleep(5)