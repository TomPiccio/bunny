#!/usr/bin/env bash
set -euo pipefail

# === Variables ===
SSH_DIR="$HOME/.ssh"
KEY_NAME="bunny_server"
HOST_ALIAS="bunny"
HOST_USER="root"
CONFIG_FILE="config.ini"
PASS_PHRASE="bunny_init"

# === Read ip_server from config.ini (ignore spaces) ===
ip_server=$(grep -i '^ip_server' "$CONFIG_FILE" | cut -d'=' -f2 | xargs)

if [[ -z "$ip_server" ]]; then
    echo "Could not read ip_server from $CONFIG_FILE"
    exit 1
fi

echo "Found ip_server: $ip_server"

# === Ensure .ssh directory exists ===
if [[ ! -d "$SSH_DIR" ]]; then
    mkdir -p "$SSH_DIR"
    echo "Created $SSH_DIR"
fi

# === Generate SSH key if it doesn't exist ===
if [[ ! -f "$SSH_DIR/$KEY_NAME" ]]; then
    echo "Generating new SSH key '$KEY_NAME' with passphrase..."
    ssh-keygen -t rsa -b 4096 -f "$SSH_DIR/$KEY_NAME" -N "$PASS_PHRASE"
fi

# === Move keys if they exist in current folder ===
if [[ -f "$KEY_NAME" ]]; then
    mv "$KEY_NAME" "$SSH_DIR/$KEY_NAME"
    echo "Moved private key to $SSH_DIR/$KEY_NAME"
fi

if [[ -f "$KEY_NAME.pub" ]]; then
    mv "$KEY_NAME.pub" "$SSH_DIR/$KEY_NAME.pub"
    echo "Moved public key to $SSH_DIR/$KEY_NAME.pub"
fi

# === Append SSH config if not already present ===
CONFIG_FILE_PATH="$SSH_DIR/config"
if ! grep -q "Host $HOST_ALIAS" "$CONFIG_FILE_PATH" 2>/dev/null; then
    {
        echo
        echo "Host $HOST_ALIAS"
        echo "    HostName $ip_server"
        echo "    User $HOST_USER"
        echo "    IdentityFile $SSH_DIR/$KEY_NAME"
    } >> "$CONFIG_FILE_PATH"
fi

echo
echo "SSH alias '$HOST_ALIAS' has been configured."
echo "You can now connect using: ssh $HOST_ALIAS"
