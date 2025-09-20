from datetime import datetime
from enum import Enum
from random import choice

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import os
import time

import serial.tools.list_ports

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


def detect_ports():
        
