#!/bin/bash

# ========================================================
# SSH Account Renewal Script for Telegram Bot
# Features:
# - Renew SSH accounts with extended expiration
# - Clean output for Telegram display
# - Error handling and validation
# ========================================================

# Configuration
SSH_DB_SOURCE="/etc/xray/ssh" # <--- Sumber utama daftar SSH (sama dengan list_ssh_users.sh)
SSH_LOG_DIR="/etc/xray/sshx/akun" # <--- Direktori log config user SSH (dari cekconfig Anda)
LOG_FILE="/var/log/ssh_renew.log"
DOMAIN=$(cat /etc/xray/domain)
IP=$(curl -sS ipv4.icanhazip.com)

# --- Input Validation ---
if [ "$#" -ne 3 ]; then
    echo "❌ Error: Invalid arguments"
    echo "Usage: $0 <username> <days_to_add> <admin_telegram_id>"
    exit 1
fi

USERNAME="$1"
DAYS="$2"
ADMIN_ID="$3"

# --- Validation Functions ---
validate_username() {
    if ! grep -q "^### $USERNAME " "$SSH_DB_SOURCE"; then
        echo "❌ Error: User $USERNAME not found in SSH accounts list."
        exit 1
    fi
}

validate_days() {
    if ! [[ "$DAYS" =~ ^[0-9]+$ ]]; then
        echo "❌ Error: Days must be a positive integer"
        exit 1
    fi
}

# --- Renewal Function ---
renew_ssh() {
    user_line=$(grep "^### $USERNAME " "$SSH_DB_SOURCE")
    
    if [ -z "$user_line" ]; then
        echo "❌ Error: User $USERNAME not found in SSH accounts list during renewal."
        exit 1
    fi

    current_exp_date_raw=$(echo "$user_line" | awk '{print $3}')
    
    new_exp_system=$(date -d "$current_exp_date_raw + $DAYS days" +"%Y-%m-%d")
    new_exp_display=$(date -d "$current_exp_date_raw + $DAYS days" +"%d %b, %Y")

    # Update entri di SSH_DB_SOURCE (mengganti seluruh baris)
    sed -i "s|^### $USERNAME .*|### $USERNAME $new_exp_system|" "$SSH_DB_SOURCE"

    # Update system account (ini penting agar akun tidak expired di OS)
    usermod -e "$new_exp_system" "$USERNAME"

    # Log the action
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Renewed $USERNAME for $DAYS days (new expiry: $new_exp_system) by Admin ID: $ADMIN_ID" >> "$LOG_FILE"
}

# --- Main Execution ---
validate_username
validate_days

if renew_ssh; then
    echo "✅ <b>SSH ACCOUNT RENEWED</b>"
    echo "============================"
    echo "<b>Username:</b> <code>$USERNAME</code>"
    echo "<b>Days Added:</b> $DAYS"
    echo "<b>New Expiry:</b> $new_exp_display"
    echo "============================"
    echo "<b>Server Info:</b>"
    echo "<b>IP:</b> $IP"
    echo "<b>Domain:</b> $DOMAIN"
    echo "============================"
    echo "<i>Renewed at: $(date '+%d %b, %Y %H:%M:%S')</i>"
else
    echo "❌ <b>RENEWAL FAILED</b>"
    echo "============================"
    echo "<b>Username:</b> <code>$USERNAME</code>"
    echo "<b>Error:</b> An unknown error occurred during renewal."
    exit 1
fi

exit 0
