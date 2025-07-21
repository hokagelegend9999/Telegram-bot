#!/bin/bash

# ========================================================
# SSH Account Renewal Script for Telegram Bot
# Features:
# - Renew SSH accounts with extended expiration
# - Clean output for Telegram display
# - Error handling and validation
# ========================================================

# Configuration
SSH_DB="/etc/ssh/.ssh.db"
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
    if ! grep -q "^#ssh# $USERNAME " "$SSH_DB"; then
        echo "❌ Error: User $USERNAME not found in database"
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
    # Get current expiration
    current_exp=$(grep "^#ssh# $USERNAME " "$SSH_DB" | awk '{print $6,$7,$8}')
    
    # Calculate new expiration date
    new_exp=$(date -d "$current_exp + $DAYS days" +"%d %b, %Y")
    new_exp_system=$(date -d "$new_exp" +"%Y-%m-%d")
    
    # Update database
    sed -i "/^#ssh# $USERNAME /d" "$SSH_DB"
    grep "^#ssh# $USERNAME " "$SSH_DB" | \
        awk -v exp="$new_exp" '{$6=$7=$8=""; print $0 exp}' >> "$SSH_DB"
    
    # Update system account
    usermod -e "$new_exp_system" "$USERNAME"
    
    # Log the action
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Renewed $USERNAME for $DAYS days by $ADMIN_ID" >> "$LOG_FILE"
}

# --- Main Execution ---
validate_username
validate_days

if renew_ssh; then
    # Prepare output message
    echo "✅ <b>SSH ACCOUNT RENEWED</b>"
    echo "============================"
    echo "<b>Username:</b> <code>$USERNAME</code>"
    echo "<b>Days Added:</b> $DAYS"
    echo "<b>New Expiry:</b> $new_exp"
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
    echo "<b>Error:</b> Unknown error occurred"
    exit 1
fi

exit 0
