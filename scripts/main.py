from flask_server import app
from web_driver import BunnyDriver
from threading import Thread
from hardware import background_process

def run_flask():
    app.run(host="0.0.0.0", port=5000, debug=True)

flask_thread = Thread(target=run_flask, daemon=True)
flask_thread.start()

serial_thread = Thread(target=background_process, daemon=True)
serial_thread.start()

_BunnyDriver = BunnyDriver()
_BunnyDriver.execute()