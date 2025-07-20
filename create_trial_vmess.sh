#!/bin/bash

# ==================================================================
#         TRIAL VMESS Creator - Telegram Friendly Format
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

# Check for duplicate
if grep -q "\"$user\"" "$CONFIG_FILE"; then
    echo "❌ Error: Gagal membuat username unik, silakan coba lagi."
    exit 1
fi

# Add to config
sed -i '/#vmess$/a\#vm '"$user $exp"'\
},{"id": "'"$uuid"'","alterId": "0","email": "'"$user"'"' "$CONFIG_FILE"
sed -i '/#vmessgrpc$/a\#vmg '"$user $exp"'\
},{"id": "'"$uuid"'","alterId": "0","email": "'"$user"'"' "$CONFIG_FILE"

# Log trial user
mkdir -p /etc/hokage-bot
EXP_TIME=$(date +%s -d "$TIMER_MINUTE minutes")
echo "${EXP_TIME}:${user}:vmess" >> "$TRIAL_LOG_FILE"

# Generate links
vmess_ws_tls_json="{\"v\":\"2\",\"ps\":\"${user} TLS\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}"
vmess_ws_nontls_json="{\"v\":\"2\",\"ps\":\"${user} NTLS\",\"add\":\"${domain}\",\"port\":\"80\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"none\"}"
vmess_grpc_json="{\"v\":\"2\",\"ps\":\"${user} gRPC\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"grpc\",\"path\":\"vmess-grpc\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}"

vmesslink1="vmess://$(echo -n "$vmess_ws_tls_json" | base64 -w 0)"
vmesslink2="vmess://$(echo -n "$vmess_ws_nontls_json" | base64 -w 0)"
vmesslink3="vmess://$(echo -n "$vmess_grpc_json" | base64 -w 0)"

# Restart service
systemctl restart xray > /dev/null 2>&1

# Beautiful Format for Telegram (without HTML)
TEXT="
═══════[ TRIAL VMESS ]═══════
🆔 Username: $user
🌐 Domain: $domain
⏳ Expired: $TIMER_MINUTE Minutes
═══════════════════════════════
📡 Server Info:
├─ 🏢 ISP: $ISP
└─ 🌆 City: $CITY
🔒 Security:
├─ 🔑 UUID: $uuid
└─ 🛡️ AlterID: 0
═══════════════════════════════
🔗 Connection Links:
┌─ 🌐 TLS (443):
│  $vmesslink1
│
├─ 🌍 NTLS (80):
│  $vmesslink2
│
└─ 🚀 gRPC (443):
   $vmesslink3
═══════════════════════════════
⚠️ Trial akan expired setelah $TIMER_MINUTE menit!
"

# Output
echo "$TEXT"
