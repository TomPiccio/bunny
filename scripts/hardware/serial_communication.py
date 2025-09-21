import serial.tools.list_ports
from typing import Callable, Any
import time
import sys
import os
import re

if __name__ == "__main__" or os.path.dirname(sys.argv[0])==os.path.dirname(__file__):
    from motion_map import MotionMap, BottomMotionMap, emoji_to_motion_map
else:
    from .motion_map import MotionMap, BottomMotionMap, emoji_to_motion_map

if os.path.dirname(sys.argv[0]) != "scripts":
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from common import shutDownProcess
from utils import setup_logger

logger = setup_logger("logs")
logger.info(f"Logger initialized inside ({os.path.splitext(os.path.basename(__file__))[0]}.py)")

_BunnyDriver = None

def set_BunnyDriver(__BunnyDriver):
    _BunnyDriver = __BunnyDriver

def HEART_PRESSED_BunnyDriver():
    _BunnyDriver.toggle_recording(True)

OpenRBProcesses= {
    cmd.name: (
        None if cmd.value is None else {
            "command": cmd.value,
            "sent": False,
            "timeout": 0,
        }
    )
    for cmd in MotionMap }

OpenRBProcesses["OPENRB_FINISHED_SETUP"] =  None

def OpenRBProcess(data=None):
    if data is not None:
        if data in OpenRBProcesses:
            if isinstance(OpenRBProcesses[data], dict):
                if OpenRBProcesses[data]["sent"]:
                    OpenRBProcesses[data]["sent"] = False
            else:
                fxn : Callable[..., Any] | None = OpenRBProcesses[data]
                fxn()

NanoProcesses = {
    cmd.name: (
        None if cmd.value is None else {
            "command": cmd.value,
            "sent": False,
            "timeout": 0,
        }
    )
    for cmd in BottomMotionMap }

NanoProcesses["LOW_BATT"] = shutDownProcess
NanoProcesses["HEART_PRESSED"] = HEART_PRESSED_BunnyDriver

def NanoProcess(data=None):
    if data is not None:
        if data in NanoProcesses:
            if isinstance(NanoProcesses[data], dict):
                if NanoProcesses[data]["sent"]:
                    NanoProcesses[data]["sent"] = False
            else:
                fxn: Callable[..., Any] | None = NanoProcesses[data]
                fxn()


Devices = {
    "OpenRB": {
        "ids": ["2F5D:2202"],
        "port": None,
        "serial": None,
        "processes": OpenRBProcess,
        "commands": OpenRBProcesses,
        "connection_check_cooldown" : 10.0,
        "active" : False,
        "prev_active" : False,
        "is_idle" : True
    },
    "Nano": {
        "ids": ["1A86:7523", "2341:805A"],
        "port": None,
        "serial": None,
        "processes": NanoProcess,
        "commands": NanoProcesses,
        "connection_check_cooldown" : 10.0,
        "active" : False,
        "prev_active" : False,
        "is_idle" : True
    }
}

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


def sendCommand(command : str, device_name: str):
    """
    This will attempt to send data to the device through serial.

    command (str): This command that will be interpreted by the device seen on the processes file
    deviceName (str): The device name which matches on the Devices Dictionary
    """
    _serial = Devices.get(device_name).get("serial")
    if _serial is None:
        logger.critical(f"{device_name} does not exist")
        return False
    try:
        if command in Devices[device_name]["commands"]:
            if isinstance(Devices[device_name]["commands"][command], dict):
                dict_focus = dict(Devices[device_name]["commands"][command])
                dict_focus["sent"] = True
                data = dict_focus.get("command")
                dict_focus["timeout"] = 1.0
                if data is not None:
                    _bytes = _serial.write((str(data) + '\n').encode())
                    logger.info("Sent: " + str(data) + " Size: " + str(_bytes) + " bytes.")
                    return True
        return False
    except Exception as e:
        logger.critical(f"Send Command Error: {e}")
        return False

def emoji_to_command(emoji: str):
    _top_motion_map, _bottom_motion_map = emoji_to_motion_map(emoji)
    if _top_motion_map != MotionMap.IDLE:
        Devices["OpenRB"]["is_idle"] = False
        sendCommand(_top_motion_map.name,"OpenRB")
    if _bottom_motion_map != BottomMotionMap.IDLE:
        Devices["Nano"]["is_idle"] = False
        sendCommand(_bottom_motion_map.name, "Nano")

def receiveData(device_name: str):
    """
    This will attempt to receive data from the device.

    device_name (str): The device name which matches on the Devices Dictionary
    """
    _serial = Devices.get(device_name).get("serial")
    if _serial is None:
        return None
    response = _serial.readline().decode().strip()
    if response:
        logger.info("Received: " + response)
        return response
    return None

def confirm_connection(device_name):
    """
    This will check if there is still an active serial connection between devices.

    device_name (str): The device name which matches on the Devices Dictionary
    """
    _serial = Devices.get(device_name).get("serial")
    if _serial is None:
        logger.critical(f"{device_name} does not exist")
        return False
    try:
        data = 100 # Request for Connection
        _bytes = _serial.write((str(data) + '\n').encode())
        logger.info("Sent: " + str(data) + " Size: " + str(_bytes) + " bytes.")
        return True
    except Exception as e:
        logger.critical(f"Send Command Error: {e}")
        return False

prev_timer = time.monotonic()
def checkTimeOut():
    global prev_timer
    curr_timer = time.monotonic()
    interval = curr_timer - prev_timer
    for device in Devices.keys():
        for command in Devices[device]["commands"].keys():
            if isinstance(Devices[device]["commands"][command], dict):
                dict_focus = dict(Devices[device]["commands"][command])
                if dict_focus["sent"]:
                    curr_timer = time.monotonic()
                    dict_focus["timeout"] -= interval
                    if dict_focus["timeout"] < 0:
                        logger.critical(f"{command} Timed Out")
                        dict_focus["sent"] = False

        if Devices[device]["connection_check_cooldown"] > 0:
            Devices[device]["connection_check_cooldown"] -= interval
        else:
            Devices[device]["connection_check_cooldown"] = 10
            if not Devices[device]["active"] and not Devices[device]["prev_active"]:
                logger.critical(f"Device {device} has no active connection.")
            Devices[device]["prev_active"] = Devices[device]["active"]
            Devices[device]["active"] = False
            confirm_connection(device)

    prev_timer = curr_timer


def background_process():
    while True:
        for device_name in Devices.keys():
            data = receiveData(device_name)
            if data:
                if data == "RESPONSE":
                    Devices[device_name]["active"] = True
                elif data == "IDLE":
                    Devices[device_name]["is_idle"] = True
                else:
                    _function = Devices[device_name]["processes"]
                    _function(data)
        checkTimeOut()

