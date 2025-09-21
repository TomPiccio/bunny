from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from datetime import datetime
from configparser import ConfigParser, ExtendedInterpolation
import http.server
import socketserver
import threading
import re
import time
import sys
import os

if __name__ == "__main__" or os.path.dirname(sys.argv[0])==os.path.dirname(__file__):
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils import setup_logger
from hardware.motion_map import emoji_to_motion

logger = setup_logger("logs")
logger.info(f"Logger initialized inside ({os.path.splitext(os.path.basename(__file__))[0]}.py)")


class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, html_file_path, *args, **kwargs):
        super().__init__(*args, directory=html_file_path, **kwargs)

class BunnyDriver:
    def __init__(self):
        self.PORT = 8006
        self.html_file_path = os.path.join(os.path.abspath(__file__), r"../../xiaozhi-esp32-server/main/xiaozhi-server/test")
        self.chromedriver_path = r"/usr/bin/chromedriver"
        self.chrome_binary_path = r"/usr/bin/chromium"
        self.alt_chromedriver_path = r"/chromedriver/chromedriver-win32/chromedriver.exe"  # update this
        self.alt_chrome_binary_path = r"D:\Downloads\chrome-win32\chrome-win32\chrome.exe"
        self.ota_server, self.web_socket = self.config_parsing()
        self.driver = None

        self.last_dt = None
        self.start = False
        self.prev_start = False
        self.audio_count = 0

    @staticmethod
    def config_parsing():
        _config = ConfigParser(interpolation=ExtendedInterpolation())
        _config.read(os.path.join(os.path.abspath(__file__),"../../config.ini"))
        section = _config["Default"]
        _ip_server = section["ip_server"]
        _ota_server = section["ota_server"].replace("{ip_server}",_ip_server)
        _web_socket = section["web_socket"].replace("{ip_server}",_ip_server)
        return _ota_server, _web_socket

    def start_server(self):
        with socketserver.TCPServer(("", self.PORT), Handler) as httpd:
            logger.info(f"Serving at http://localhost:{self.PORT}")
            httpd.serve_forever()

    def init_driver(self):
        try:
            server_thread = threading.Thread(target=self.start_server, daemon=True)
            server_thread.start()

            time.sleep(2)

            # Make it a proper file URL
            file_url = f"http://localhost:8006/{os.path.abspath(self.html_file_path)}"

            # === Chrome options ===
            options = Options()
            options.binary_location = self.chrome_binary_path
            options.add_argument("--no-sandbox")
            options.add_argument("--user-data-dir={/home/bmopi/.config/chromium/SeleniumProfile}")
            service = Service(self.chromedriver_path)
            self.driver = webdriver.Chrome(service=service, options=options)

            # === Open the HTML file ===
            self.driver.get(file_url)
            successful_launch = True
        except Exception as _e:
            logger.error(_e)
            successful_launch = False
        return successful_launch

    def write_input_field(self, x_path: str, input_text: str) -> None:
        input_field = self.driver.find_element(By.XPATH, x_path)
        input_field.clear()
        input_field.send_keys(input_text)
        time.sleep(0.5)

    def click_button(self, x_path: str, button_text: str | None = None) -> None:
        button = self.driver.find_element(By.XPATH, x_path)
        print(button.text)
        if button_text is None or button.text == button_text:
            button.click()
            time.sleep(0.5)
        elif button_text is not None:
            logger.warning(f"{button_text} not found")


    def send_message(self, message):
        self.click_button("/html/body/div/div[4]/div[1]/button[1]", "文本消息") # Text Message Menu
        self.write_input_field("/html/body/div/div[4]/div[2]/div/input", message) # Send Text Hello
        self.click_button("/html/body/div/div[4]/div[2]/div/button", "发送") # Send Message

    def toggle_recording(self, toggle : bool):
        self.click_button("/html/body/div/div[4]/div[1]/button[2]", "语音消息")  # Voice Message Menu
        # Start Recording: "开始录音" Stop Recording: "停止录音"
        self.click_button("/html/body/div/div[4]/div[3]/div/button", "开始录音" if toggle else "停止录音")

    def initial_navigation(self):
        self.write_input_field("/html/body/div/div[3]/div/input[1]", self.ota_server)
        self.write_input_field("/html/body/div/div[3]/div/input[2]", self.web_socket)
        self.click_button("/html/body/div/div[3]/div/button[1]", "连接") # Connect to WS driver
        self.toggle_recording(True)
        self.send_message("你好") # Hello

    @staticmethod
    def parse_timestamp(_text, _last_dt=None):
        """
           Parse timestamp like [23:59:59.123]
           Adjusts day rollover based on _last_dt.
        """

        try:
            m = re.search(r"\[(\d+):(\d+):(\d+)\.(\d+)\]", _text.lower())
            if not m:
                return None

            hour, minute, second, millis = map(int, m.groups())

            # Start with same date as _last_dt if available
            base_date = datetime(2000, 1, 1)
            if _last_dt:
                base_date = _last_dt.replace(hour=0, minute=0, second=0, microsecond=0)

            _ts = base_date.replace(hour=hour, minute=minute, second=second, microsecond=millis * 1000)

            # If _ts is earlier than _last_dt, assume midnight rollover → add one day
            if hour == 0 and _last_dt.hour > hour:
                _ts = _ts.replace(day=_last_dt.day + 1)

            return _ts
        except Exception as _e:
            print(_e)
            return None

    def process_text(self, _text):
        try:
            if '大模型回复' in _text:
                logger.info(_text[-1])
                emoji_to_motion(_text[-1])
                self.start = True
            elif '服务器发送语音段: undefined' in _text:
                self.start = False
                if self.audio_count == 0:
                    logger.error("No audio played")
                    self.audio_count = 0
            elif '开始播放' in _text and self.start:
                self.audio_count += 1
            elif ":" in _text.split("]")[-1]:
                if not "undefined" in _text:
                    logger.info(_text.split(":")[-1])
            self.prev_start = self.start
        except Exception as _e:
            logger.error(_e)
            return None

    def clear_processed_logs(self, keep_last_n=0):
        self.driver.execute_script(f"""
          let logContainer = document.getElementById("logContainer");
          if (logContainer) {{
           let total = logContainer.children.length;
           for (let i = 0; i < total - {keep_last_n}; i++) {{
            logContainer.removeChild(logContainer.firstChild);
           }}
          }}
         """)

    def close_driver(self):
        try:
            self.toggle_recording(False)
        except KeyboardInterrupt as e:
            logger.info("Can't stop recording")
        # === Close ===
        self.driver.quit()

    def execute(self):
        successful_launch =self.init_driver()
        if successful_launch:
            try:
                self.initial_navigation()
                while True:
                    log_entries = self.driver.find_elements(By.CSS_SELECTOR, "#logContainer .log-entry")
                    for entry in log_entries:
                        if not entry.text:
                            continue
                        text = entry.text.strip()
                        ts = self.parse_timestamp(text, self.last_dt)
                        if ts and (self.last_dt is None or ts > self.last_dt):
                            self.process_text(text)
                            self.last_dt = ts
                    self.clear_processed_logs(50)

                    time.sleep(0.5)
            except KeyboardInterrupt as e:
                self.close_driver()

#TODO: Play initial Audio
