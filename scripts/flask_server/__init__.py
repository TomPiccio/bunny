# app/__init__.py
from flask import Flask
from .app import register_routes
import sys
import os

if os.path.basename(sys.argv[0]) != "main.py":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils import setup_logger

logger = setup_logger("logs")
logger.info("Logger initialized inside app package")

if os.path.basename(sys.argv[0]) == "main.py":
    app = Flask(__name__)
    register_routes(app, logger)  # register routes from app.py
else:
    app = None
    logger.info("Current caller is not main.py. Hence, flask server is not re-performed")

