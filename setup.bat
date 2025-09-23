@echo off
setlocal enabledelayedexpansion

REM === Variables ===
set SSH_DIR=%USERPROFILE%\.ssh
set KEY_NAME=bunny_server
set HOST_ALIAS=bunny
set HOST_USER=root
set CONFIG_FILE=config.ini
set PASS_PHRASE=bunny_init


REM === Read ip_server from config.ini (ignore spaces) ===
for /f "tokens=1* delims==" %%A in ('findstr /i "^ip_server" "%CONFIG_FILE%"') do (
    set raw_ip=%%B
)

REM === Trim spaces from raw_ip ===
for /f "tokens=* delims= " %%C in ("!raw_ip!") do set ip_server=%%C
if "%ip_server%"=="" (
    echo Could not read ip_server from %CONFIG_FILE%
    exit /b 1
)

echo Found ip_server: %ip_server%

REM === Ensure .ssh directory exists ===
if not exist "%SSH_DIR%" (
    mkdir "%SSH_DIR%"
    echo Created %SSH_DIR%
)

REM === Generate SSH key if it doesn't exist ===
if not exist "%SSH_DIR%\%KEY_NAME%" (
    echo Generating new SSH key "%KEY_NAME%" with passphrase "%PASS_PHRASE%"...
    ssh-keygen -t rsa -b 4096 -f "%SSH_DIR%\%KEY_NAME%" -N "%PASS_PHRASE%"
)

REM === Move keys if they exist in current folder ===
if exist "%KEY_NAME%" (
    move "%KEY_NAME%" "%SSH_DIR%\%KEY_NAME%"
    echo Moved private key to %SSH_DIR%\%KEY_NAME%
)
if exist "%KEY_NAME%.pub" (
    move "%KEY_NAME%.pub" "%SSH_DIR%\%KEY_NAME%.pub"
    echo Moved public key to %SSH_DIR%\%KEY_NAME%.pub
)

REM === Append SSH config ===
echo.>> "%SSH_DIR%\config"
echo Host %HOST_ALIAS%>> "%SSH_DIR%\config"
echo     HostName %ip_server%>> "%SSH_DIR%\config"
echo     User %HOST_USER%>> "%SSH_DIR%\config"
echo     IdentityFile %SSH_DIR%\%KEY_NAME%>> "%SSH_DIR%\config"

echo.
echo SSH alias "%HOST_ALIAS%" has been configured.
echo You can now connect using: ssh %HOST_ALIAS%
pause
endlocal
