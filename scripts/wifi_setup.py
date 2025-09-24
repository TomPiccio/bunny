from flask import Flask, request, render_template_string
import socket
import os


def has_internet(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except Exception:
        return False
app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html>
<body>
  <h2>Bunny Wi-Fi Setup</h2>
  <form action="/save" method="post">
    SSID: <input type="text" name="ssid"><br><br>
    Password: <input type="password" name="password"><br><br>
    <input type="submit" value="Save">
  </form>
</body>
</html>
"""

@app.route("/")
def index():
    return HTML_FORM

@app.route("/save", methods=["POST"])
def save():
    ssid = request.form["ssid"]
    password = request.form["password"]

    wpa_conf = f"""
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""
    with open("/etc/wpa_supplicant/wpa_supplicant.conf", "w") as f:
        f.write(wpa_conf)

    os.system("sync")
    os.system("reboot")
    return "Saved! Rebooting..."

def run_flask_wifi_setup():
    app.run(host="0.0.0.0", port=80)
