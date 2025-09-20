from flask import Flask, request
import signal
import time
import sys
import os
print("app",sys.path)
if os.path.dirname(sys.argv[0]) != "scripts":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
print("app",sys.path)
from utils import setup_logger
from hardware import sendCommand

logger = setup_logger("logs")
logger.info(f"Logger initialized inside ({os.path.splitext(os.path.basename(__file__))[0]}.py)")



def register_routes(app, logger):
    @app.route('/move', methods=['GET'])
    def move():
        direction = request.args.get('direction')
        logger.info(f"[SIMULATION] Moving {direction}")
        return f"Robot moving {direction}", 200


    @app.route('/heartbeat')
    def heartbeat():
        result = sendCommand("HEARTPUMP", "Nano")
        if not result:
            logger.critical("Command not Sent")
        logger.info("[SYSTEM] Heartbeat received")
        return "Heartbeat OK"


    @app.route('/power', methods=['GET'])
    def power_control():
        action = request.args.get('action')
        if action == 'off':
            logger.info("[SYSTEM] Shutdown command received")
            shutDownProcess()
            return "Shutdown initiated", 200
        if action == 'status':
            return f"Power state: {"On" if power_state else "Off"}", 200
        return "Invalid power action!", 400


    @app.route('/volume')
    def volume_control():
        level = request.args.get('level', type=int)
        if level is not None and 0 <= level <= 100:
            logger.info(f"[AUDIO] Volume set to {level}%")
            if RPiActive:
                os.system(f"amixer sset 'Master' {level}%")
            return f"Volume set to {level}%"
        return "Invalid volume level"