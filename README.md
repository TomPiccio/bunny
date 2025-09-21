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
setup.bat
ssh-copy-id -i ~/.ssh/bunny_server.pub root@<ip-address>
```
