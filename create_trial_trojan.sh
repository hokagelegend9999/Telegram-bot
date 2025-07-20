#!/bin/bash
set -e

# ==================================================================
#         ENHANCED TROJAN TRIAL CREATOR (Telegram Optimized)
# ==================================================================

TIMER_MINUTE="60"
TRIAL_LOG_FILE="/etc/hokage-bot/trial_users.log"

# Server variables
domain=$(cat /etc/xray/domain)
ISP=$(cat /etc/xray/isp)
CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid)
exp=$(date -d "0 days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"

# Generate random username
user="trial-$(tr -dc A-Z0-9 </dev/urandom | head -c 5)"

# Check for duplicates
if grep -q -w "$user" "$CONFIG_FILE"; then
    echo "ERROR: Username already exists"
    exit 1
fi

# Add to config
sed -i '/#trojanws$/a\#tr '"$user $exp $uuid"'\
},{"password": "'"$uuid"'","email": "'"$user"'"' "$CONFIG_FILE"
sed -i '/#trojangrpc$/a\#trg '"$user $exp"'\
},{"password": "'"$uuid"'","email": "'"$user"'"' "$CONFIG_FILE"

# Schedule deletion
mkdir -p /etc/hokage-bot
EXP_TIME=$(date +%s -d "$TIMER_MINUTE minutes")
echo "${EXP_TIME}:${user}:trojan" >> "$TRIAL_LOG_FILE"

# Generate links
trojanlink1="trojan://${uuid}@${domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni=${domain}#${user}"
trojanlink2="trojan://${uuid}@${domain}:443?path=%2Ftrojan-ws&security=tls&host=${domain}&type=ws&sni=${domain}#${user}"

# Restart service
systemctl restart xray > /dev/null 2>&1

# Generate Telegram-friendly output
cat <<EOF
===START_TROJAN_TRIAL===
🛡️ *TRIAL TROJAN PREMIUM* 🛡️
━━━━━━━━━━━━━━━━━
🔸 *Username*: \`$user\`
🔸 *Domain*: \`$domain\`
🔸 *Expired*: $TIMER_MINUTE Minutes
━━━━━━━━━━━━━━━━━
🔐 *Credentials*:
├─ 🔑 *Password*: \`$uuid\`
├─ 🌐 *ISP*: $ISP
└─ 🏙️ *City*: $CITY
━━━━━━━━━━━━━━━━━
🛠️ *Configuration*:
├─ 📍 *Path WS*: \`/trojan-ws\`
└─ ⚙️ *ServiceName*: \`trojan-grpc\`
━━━━━━━━━━━━━━━━━
🔗 *Connection Links*:
┌─ 🌐 *WS TLS*:
│  \`$trojanlink2\`
│
└─ 🚀 *gRPC*:
   \`$trojanlink1\`
━━━━━━━━━━━━━━━━━
⚠️ *Note*: Auto-deletes after $TIMER_MINUTE minutes
===END_TROJAN_TRIAL===
EOF

# Create log file
LOG_DIR="/etc/trojan/akun"
mkdir -p "$LOG_DIR"
cat <<EOF > "${LOG_DIR}/log-create-${user}.log"
🛡️ TRIAL TROJAN ACCOUNT 🛡️
=========================
Username: $user
Domain: $domain
Password: $uuid
Expired: $TIMER_MINUTE minutes
=========================
EOF

exit 0
