# Bunny

## Raspberry Pi Setup

Copy the `config_template.ini` and edit the server_ip field

```shell
[Default]
ip_server = XXX.XXX.XXX.XXX
#Update the ip_server address above
ota_server = http://{ip_server}:8003/xiaozhi/ota/
web_socket = ws://{ip_server}:8000/xiaozhi/v1/
```
Open the terminal and run the following after replacing the <ip-address> to the correct address.

```shell
sudo apt update
sudo apt install chromium-browser chromium-chromedriver
sudo usermod -a -G dialout $USER
chmod +x setup.sh
./setup.sh
setup.bat
ssh-copy-id -i ~/.ssh/bunny_server.pub root@<ip-address>
```

When running the main.py for the first time. It might need to allow the microphone permission and the code will save this preference to be used on the next runs.

## Project File Structure

```
├── docs
│   └── .md files for documentation*
├── scripts
│   ├── Bottom_Arduino_Code (OPENRB-150 Arduino Code)
│   │   ├── AX8601.cpp (C++ code for the AX8601 Servo Motors)
│   │   ├── AX8601.h (C++ header for AX8601.cpp)
│   │   └── Bottom_Arduino_Code.ino
│   ├── Bunny_Final_v3 (OPENRB-150 Arduino Code)
│   │   ├── AX8601.cpp (C++ code for the AX8601 Servo Motors)
│   │   ├── AX8601.h (C++ header for AX8601.cpp)
│   │   ├── Bunny_Final_v3.ino (MAIN ARDUINO FILE)
│   │   ├── EarsDynamixel.cpp (C++ code for the Dynamixel Motors)
│   │   ├── EarsDynamixel.h (C++ header for EarsDynamixel.cpp)
│   │   ├── Motions.cpp (C++ code to translate emotion to motion)
│   │   └── Motions.h (C++ header for Motions.cpp)
│   ├── flask_server
│   │   └── app.py (allows the phone app to communicate to the robot)
│   ├── hardware
│   │   ├── motion_map.py (contains the Enums and Dictionaries mapping emotion to motion)
│   │   └── serial_communication.py (communicates to both microcontrollers thru serial to control the hardware)
│   ├── utils
│   │   ├── audios
│   │   │   ├── script.md - you can check the different text version of the audoi for different states
│   │   │   └── ... mp3 audio files* (offline headless indicators of the current status)
│   │   ├── audio_player.py (This contains the functions to run)
│   │   └── logger.py (This manages the .log files to be able to check traceback upto 5MB)
│   ├── web_driver
│   │   └── driver.py (runs the browser that 
│   ├── common.py (common methods to prevent circular references)
│   └── main.py (<- MAIN FILE BEING RAN by 'bunny' alias)
├── logs (contains up to 5 files of logs 1MB each)
├── xiaozhi-esp32-server (a submodule that allows the html code to run)
│   └── main/xiaozhi-server/test/test_page.html
├── README.md (Current file to be read fully before starting)
├── config.ini (This has to be created manually!)
├── config_template.ini (refer to this to create config.ini above)
├── requirements.txt (python libraries to be downloaded by setup.bat / setup.sh)
├── setup.bat (Run first for Windows) <- See Raspberry Pi Setup above
└── setup.sh (Run first for Linux) <- See Raspberry Pi Setup above
```

> \* Grouped some files together excluding git, cache, and irrelevant files.
> 
> excludes git, cache, and irrelevant files.


## Important Notes

### main.py

This file integrates all the different parts of the project running concurrently.

Here are the processes occurring at the same time:

1. `AudioPlayer()` - plays staus audio files
2. `BunnyDriver()` - a webdriver that navigates the xiaozhi-server
   * `BunnyDriver.init_driver()` - runs a server to allow the `test_page.html` to run (`http://localhost:8006`)
   * `BunnyDriver.execute()` - uses a webdriver to navigate the `test_page.html`
3. SSH (Cloud Server) `run_remote_bunny()` - run the `bunny` alias on the cloud
4. Flask / phone app integration `run_flask()`
5. active heartbeat `heartbeat_fn()` - sends a signal every 10s to indicate to the app that it is active using SYSTEM_UUID
6. serial hardware communication `hardware.background_process()`
7. logger - to take a log on what occurs during execution (can be used for debugging)

These multiple processes makes this project very complicated!

### serial_communication.py

*From: scripts/hardware/*

This detects the two connections. It always assumes that the top circuit has the OpenRB-150 having the capabilities  to control the Dynamixel Servo Motors.
The bottom is a generic Arduino Nano able to communicate with the body servos and the heart. These microcontrollers are detected based on
port_hwid. Note, however, that Arduino Nano can have multiple versions. Hence, don't forget to include the appropriate port_hwid.

The dictionary below allows the code to segment the two microcontrollers almost simultaneously.

```python
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
        "ids": ["1A86:7523", "2341:805A", "2341:8057"],
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
```

### motion_map.py

*From: scripts/hardware/*

The motion maps below allow the Enums that make the code more readable over all. It is separated to the top and bottom
microcontrollers.

The AI chatbot communicates emotion via emoticons. Hence, this is used to be translated to motion via some semi-random map.

```python
class MotionMap(Enum):
    '''
    Motion for the OpenRB Top Arduino
    '''
    IDLE = 0
    RAISE_EAR = 1
    COVER_EYES = 2
    FORWARD_EAR = 3
    BEND_EAR = 4
    FLAP_EAR = 5 # Flap the lower ear
    NOD = 6
    SHAKE = 7
    PET = 8
    SAD_SHAKE = 9 # Bend Down Hand and shake
    BEND_HEAD = 10
    EAR_WAVE = 11 # Slowly wave the lower portion of the Ears
    DROP_EARS = 12 # Raise Ear slowly and drop it
    SLOW_NOD  = 13
    DETACH = -1

class BottomMotionMap(Enum):
    '''
    Motion for the Bottom Arduino
    '''
    IDLE = 0
    FLUTTER_KICK = 1
    HEART_PUMP = 2
    TOGGLE_SIT_STAND = 3
    STAND = 4
    SIT = 5

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

#Based on the xiaozhi-esp32-server\main\xiaozhi-server\core\utils\textUtils.py
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
```

### logger.py

*From: scripts/utils/*

Important to combine the logs into the logs folder for all the different scripts

```python
from utils import setup_logger

_logger = setup_logger("logs")
_logger.info(f"Logger initialized inside ({os.path.splitext(os.path.basename(__file__))[0]}.py)")

```

### audio_player.py

*From: scripts/utils/*

Here are the five audio statuses and it randomizes between 3 audio files.

```python
class Audio(Enum):
    WAKEUP = "wakeup"
    READY = "ready"
    ERROR = "error"
    WIFI = "wifi"
    SLEEP = "sleep"
    REST = "rest"
```

### setup.sh / setup.bat

This file setups the python virtual environment (.venv) and uses the config.ini file to allow ssh to occur without the need of
typing the password everytime. 


# Software Recommendations

1. Instead of relying on just python threading, use ROS2 instead for more efficient performance of the different processes.
2. The personality is mainly happy,a nd cheerful and thus, mostly replies positive emotions making it difficult to map
it into motion relying only on the emojis. A situation where the personality acts positively to cher up the recipient.
There is barely an emotion to equate to comforting motions which the bot is made for.
3. There is a wifi_setup/wifi_setup_new branch that attempts to use the RaspberryPi built-in Wi-Fi hotspot to allow phones to connect
to said network and transmit Wi-Fi credentials as setup. With this feature, the robot can connect to another Wi-Fi 
network remotely without the need of typing through a keyboard and monitor.
4. If the code works properly, the following can be done to allow the code to run independently after powering up.
This has been set up to the first prototype but there are still some bugs that causes the code to input wrong URLs to the test_page.html.

```bash
mkdir -p ~/.config/autostart
nano ~/.config/autostart/bunny.desktop
```

Write this into said file:
```text
[Desktop Entry]
Type=Application
Name=Bunny
Exec=/home/bmopi/Desktop/bunny/.venv/bin/python /home/bmopi/Desktop/bunny/scripts/main.py
StartupNotify=false
Terminal=true
```

> Note: `bmopi` is the username of the RPi. Change it accordingly.

Press `Ctrl+O -> Save` and `Ctrl+X -> Exit`