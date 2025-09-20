from datetime import datetime
from enum import Enum
from random import choice
from typing import Any, Callable
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

import signal
import sys
import serial.tools.list_ports
import re
import threading
from flask import Flask, request
import logging
from logging.handlers import RotatingFileHandler
import coloredlogs

debug = False
_logging = True
RPiActive = False
_shouldIShutDown = False

# region Motion Mapping
class MotionMap(Enum):
    IDLE = 1
    RAISE_EAR = 2
    COVER_EYES = 3
    BEND_EAR = 4
    FLAP_EAR = 5 # Flap the lower ear
    NOD = 6
    SHAKE = 7
    PET = 8
    SAD_SHAKE = 9 # Bend Down Hand and shake
    BEND_HEAD = 10
    EAR_WAVE = 11 # Slowly wave the lower portion of the Ears
    DROP_EARS = 12 # Raise Ear slowly and drop it
    SLOW_NOD = 13
    DETACH = -1

class EmotionMap(Enum):
    IDLE = 0
    HAPPY = 1
    SAD = 2
    DENY = 3
    AFFIRM = 4
    ANGRY = 5
    CRYING = 6
    SHY = 7
    SLEEPY = 8
    RELAXED = 9
    COMFORT = 10

EMOTION_TO_MOTION_MAP = {
    EmotionMap.IDLE : [MotionMap.IDLE],
    EmotionMap.HAPPY : [MotionMap.FLAP_EAR, MotionMap.NOD, MotionMap.RAISE_EAR],
    EmotionMap.SAD : [MotionMap.SAD_SHAKE, MotionMap.BEND_HEAD, MotionMap.DROP_EARS],
    EmotionMap.AFFIRM: [MotionMap.NOD, MotionMap.BEND_EAR],
    EmotionMap.DENY: [MotionMap.SHAKE, MotionMap.SAD_SHAKE],
    EmotionMap.ANGRY: [MotionMap.SHAKE, MotionMap.BEND_EAR, MotionMap.DROP_EARS],
    EmotionMap.CRYING: [MotionMap.COVER_EYES, MotionMap.BEND_HEAD],
    EmotionMap.SHY: [MotionMap.COVER_EYES, MotionMap.RAISE_EAR],
    EmotionMap.SLEEPY: [MotionMap.BEND_HEAD],
    EmotionMap.RELAXED: [MotionMap.IDLE, MotionMap.EAR_WAVE],
    EmotionMap.COMFORT: [MotionMap.PET, MotionMap.SAD_SHAKE, MotionMap.BEND_HEAD, MotionMap.SLOW_NOD]
}


EMOJI_MAP = {
    "😂": ("laughing",EmotionMap.HAPPY),
    "😭": ("crying",EmotionMap.SAD),
    "😠": ("angry",EmotionMap.ANGRY),
    "😔": ("sad",EmotionMap.SAD),
    "😍": ("loving",EmotionMap.COMFORT),
    "😲": ("surprised",EmotionMap.HAPPY),
    "😱": ("shocked",EmotionMap.DENY),
    "🤔": ("thinking",EmotionMap.HAPPY),
    "😌": ("relaxed",EmotionMap.RELAXED),
    "😴": ("sleepy",EmotionMap.SLEEPY),
    "😜": ("silly",EmotionMap.HAPPY),
    "🙄": ("confused",EmotionMap.SLEEPY),
    "😶": ("neutral",EmotionMap.IDLE),
    "🙂": ("happy",EmotionMap.HAPPY),
    "😆": ("laughing",EmotionMap.HAPPY),
    "😳": ("embarrassed",EmotionMap.SHY),
    "😉": ("winking",EmotionMap.HAPPY),
    "😎": ("cool",EmotionMap.AFFIRM),
    "🤤": ("delicious",EmotionMap.AFFIRM),
    "😘": ("kissy",EmotionMap.HAPPY),
    "😏": ("confident",EmotionMap.AFFIRM),
}

def emoji_to_motion(emoji : str) -> MotionMap:
     if emoji in EMOJI_MAP:
         actions = EMOTION_TO_MOTION_MAP[EMOJI_MAP[emoji][1]]
         return choice(actions)
     return MotionMap.IDLE

# endregion

# === Path to your HTML file ===
html_file_path = r"D:\Documents\GitHub\xiaozhi-esp32-server\main\xiaozhi-server\test\test_page.html"  # Windows example
# For Linux, use something like "/home/pi/file.html"

# Make it a proper file URL
file_url = "file:///" + os.path.abspath(html_file_path).replace("\\", "/")

# === Path to chromedriver ===
chromedriver_path = r"/chromedriver/chromedriver-win32/chromedriver.exe"  # update this
chrome_binary_path = r"D:\Downloads\chrome-win32\chrome-win32\chrome.exe"

# === Chrome options ===
options = Options()
options.binary_location = chrome_binary_path
options.add_argument("--use-fake-ui-for-media-stream")  # auto-allow mic
options.add_argument("--no-sandbox")

service = Service(chromedriver_path)
driver = webdriver.Chrome(service=service, options=options)

# === Open the HTML file ===
driver.get(file_url)

def write_input_field(x_path : str, input_text : str) -> None:
    input_field = driver.find_element(By.XPATH, x_path)
    input_field.clear()
    input_field.send_keys(input_text)

def click_button(x_path : str, button_text : str | None = None) -> None:
    button = driver.find_element(By.XPATH, x_path)
    print(button.text)
    if button_text is None or button.text == button_text:
        button.click()

write_input_field("/html/body/div/div[3]/div/input[1]","http://47.84.198.143:8003/xiaozhi/ota/")

time.sleep(2)

write_input_field("/html/body/div/div[3]/div/input[2]","ws://47.84.198.143:8000/xiaozhi/v1/")


time.sleep(2)

click_button("/html/body/div/div[3]/div/button[1]", "连接")

time.sleep(3)

click_button("/html/body/div/div[4]/div[1]/button[2]", "语音消息")

time.sleep(3)

click_button("/html/body/div/div[4]/div[3]/div/button", "开始录音")
time.sleep(3)

click_button("/html/body/div/div[4]/div[1]/button[1]", "文本消息")
time.sleep(3)

write_input_field("/html/body/div/div[4]/div[2]/div/input","你好")
time.sleep(1)
click_button("/html/body/div/div[4]/div[2]/div/button", "发送")
                                     
last_dt = None

def parse_timestamp(_text):
    # Example text: [1:13:51 am.746]
    import re
    m = re.search(r"\[(\d+):(\d+):(\d+)\s*(am|pm)\.(\d+)\]", _text.lower())
    if not m:
        return None
    hour, minute, second, ampm, millis = m.groups()
    hour = int(hour)
    minute = int(minute)
    second = int(second)
    millis = int(millis)
    if ampm == "pm" and hour != 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    return datetime(2000, 1, 1, hour, minute, second, millis*1000)  # dummy date

start = False
prev_start = False
audio_count = 0
def process_text(_text):
    global start, prev_start, audio_count
    if '大模型回复' in _text:
        print(_text[-1])
        start = True
    elif '服务器发送语音段: undefined' in text:
        start = False
        if audio_count == 0:
            print("No audio played")
        audio_count = 0
    elif '开始播放' in _text and start:
        audio_count += 1
    #DEBUG
    # if start !=prev_start:
    #     print(start)
    prev_start = start

try:
    while True:
        log_entries = driver.find_elements(By.CSS_SELECTOR, "#logContainer .log-entry")   n
        for entry in log_entries:
            text = entry.text.strip()
            ts = parse_timestamp(text)
            if ts and (last_dt is None or ts > last_dt):
                process_text(text)
                last_dt = ts
        time.sleep(0.5)
except KeyboardInterrupt as e:
    click_button("/html/body/div/div[4]/div[3]/div/button")
    # === Example: wait or interact ===
    input("Press Enter to quit...")  # Keeps browser open

    # === Close ===
    driver.quit()

# region Logging

# Ensure log directory exists
os.makedirs("logs", exist_ok=True)

# Configure logging
logger = logging.getLogger("BunnyLog")
logger.setLevel(logging.DEBUG if _logging else logging.INFO)

# Remove default handlers (if any)
for handler in logger.handlers[:]:
    logger.removeHandler(handler)

# Rotating file handler: 1 MB per file, keep 5 backups
handler = RotatingFileHandler("logs/app.log", maxBytes=1_000_000, backupCount=5)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)

# Add handler (avoid adding multiple times if reused)
if not logger.handlers:
    logger.addHandler(handler)

# Colored console handler (using coloredlogs)
coloredlogs.install(level='DEBUG' if _logging else 'INFO', logger=logger)

# Prevent log messages from propagating to the root logger
logger.propagate = False

# endregion

# region Arduino_Pi_Integration

Devices = {
    "OpenRB": {
        "ids": ["2F5D:2202"],
        "port": None,
        "serial": None,
        "processes": None,
        "commands": None
    },
    "Nano": {
        "ids": ["1A86:7523", "2341:805A"],
        "port": None,
        "serial": None,
        "processes": None,
        "commands": None
    }
}


# region Serial Functions

def check_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        logger.critical("No serial devices found.")
        return

    for port in ports:
        match = re.search(r'VID:PID=([0-9A-Fa-f]+:[0-9A-Fa-f]+)', port.hwid).group(1)
        for device in Devices.keys():
            for id in Devices[device]["ids"]:
                if match == id:
                    if Devices[device]["port"] == None:
                        Devices[device]["port"] = port.device
                        break
            else:
                logger.info(f"{port} does not match any of the IDs. ({match})")

    for device, details in Devices.items():
        port = details["port"]
        if port:
            ser = open_serial_connection(port)
            if ser:
                details["serial"] = ser


def open_serial_connection(port, baudrate: int = 115200, timeout: int = 1):
    """
    This will attempt to open the serial channel.

    port:
    baudrate (int): This command that will be interpreted by the device
    timeout (int): Timeout
    """
    try:
        ser = serial.Serial(port, baudrate=baudrate, timeout=timeout)
        logger.info(f"Connected to {port}")
        return ser
    except serial.SerialException as e:
        logger.critical(f"Error opening serial port {port}: {e}")
        return None


def sendCommand(command: str, deviceName: str):
    """
    This will attempt to send data to the device through serial.

    command (str): This command that will be interpreted by the device seen on the processes file
    deviceName (str): The device name which matches the on on the Devices Dictionary
    """
    _serial = Devices.get(deviceName).get("serial")
    if _serial == None:
        logger.critical(f"{deviceName} does not exist")
        return False
    try:
        if command in Devices[deviceName]["commands"]:
            if isinstance(Devices[deviceName]["commands"][command], dict):
                Devices[deviceName]["commands"][command]["sent"] = True
                data = Devices[deviceName]["commands"][command].get("command")
                Devices[deviceName]["commands"][command]["timeout"] = 1.0
                if data != None:
                    bytes = _serial.write((str(data) + '\n').encode())
                    logger.info("Sent: " + str(data) + " Size: " + str(bytes) + " bytes.")
                    return True
        return False
    except Exception as e:
        logger.critical(f"Send Command Error: {e}")
        return False


def recieveData(deviceName: str):
    """
    This will attempt to recieve data from the device.

    deviceName (str): The device name which matches the on on the Devices Dictionary
    """
    _serial = Devices.get(deviceName).get("serial")
    if _serial == None:
        return None
    response = _serial.readline().decode().strip()
    if response:
        logger.info("Received: " + response)
        return response

# endregion

power_state = True


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


OpenRBProcesses = {
    cmd.name: (
        None if cmd.value is None else {
            "command": cmd.value,
            "sent": False,
            "timeout": 0,
        }
    )
    for cmd in OpenRBCommand }

OpenRBProcesses["OPENRB_FINISHED_SETUP"] =  None,
}


def OpenRBProcess(data=None):
    if data != None:
        if data in OpenRBProcesses:
            if isinstance(OpenRBProcesses[data], dict):
                if OpenRBProcesses[data]["sent"]:
                    OpenRBProcesses[data]["sent"] = False
            else:
                OpenRBProcesses[data]()


NanoProcesses = {
    "LOW_BATT": shutDownProcess,
    "FLUTTERKICK": {"command": 1, "sent": False, "timeout": 0},
    "HEARTPUMP": {"command": 2, "sent": False, "timeout": 0},
    "TOGGLESITSTAND": {"command": 3, "sent": False, "timeout": 0},
    "STAND": {"command": 4, "sent": False, "timeout": 0},
    "SIT": {"command": 5, "sent": False, "timeout": 0},
}


def NanoProcess(data=None):
    if data != None:
        if data in NanoProcesses:
            if isinstance(NanoProcesses[data], dict):
                if NanoProcesses[data]["sent"]:
                    NanoProcesses[data]["sent"] = False
            else:
                NanoProcesses[data]()


def init_Arduino_Pi_Integration():
    Devices["OpenRB"]["processes"] = OpenRBProcess
    Devices["OpenRB"]["commands"] = OpenRBProcesses
    Devices["Nano"]["processes"] = NanoProcess
    Devices["Nano"]["commands"] = NanoProcesses


prev_timer = time.monotonic()


def checkTimeOut():
    global prev_timer
    curr_timer = time.monotonic()
    for device in Devices.keys():
        for command in Devices[device]["commands"].keys():
            if isinstance(Devices[device]["commands"][command], dict):
                if Devices[device]["commands"][command]["sent"]:
                    curr_timer = time.monotonic()
                    interval = curr_timer - prev_timer
                    Devices[device]["commands"][command]["timeout"] = Devices[device]["commands"][command][
                                                                          "timeout"] - interval
                    if Devices[device]["commands"][command]["timeout"] < 0:
                        interval = curr_timer - prev_timer
                        logger.critical(f"{command} Timed Out")
                        Devices[device]["commands"][command]["sent"] = False
    prev_timer = curr_timer

def background_process():
    while True:
        for device_name in Devices.keys():
            data = recieveData(device_name)
            if data:
                _function : Callable[...,Any] = Devices[device_name]["processes"]
                _function(data)
        checkTimeOut()


# endregion

# region Flask_Server
app = Flask(__name__)


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

# endregion
import time
from selenium.webdriver.common.by import By

last_dt = None

def run_log_monitor(driver):
    global last_dt
    try:
        while True:
            _log_entries = driver.find_elements(By.CSS_SELECTOR, "#logContainer .log-entry")
            for _entry in _log_entries:
                text = _entry.text.strip()
                ts = parse_timestamp(text)
                if ts and (last_dt is None or ts > last_dt):
                    process_text(text)
                    last_dt = ts
            time.sleep(0.5)
    except KeyboardInterrupt:
        click_button("/html/body/div/div[4]/div[3]/div/button")
        input("Press Enter to quit...")  # Keeps browser open before exit
        driver.quit()


if __name__ == "__main__":
    run_log_monitor(driver)
