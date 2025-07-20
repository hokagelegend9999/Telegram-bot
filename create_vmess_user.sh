#!/bin/bash

# ==================================================================
#         VMESS Account Creator - Telegram Friendly Format
# ==================================================================

# Error handling
if [ "$#" -lt 2 ]; then
    echo "⚠️  Error: Butuh minimal 2 argumen: <user> <masa_aktif> [ip_limit] [kuota_gb]"
    echo "Usage: $0 <username> <days> [ip_limit] [quota_gb]"
    exit 1
fi

# Set defaults
user="$1"
masaaktif="${2:-1}"    # Default 1 day
iplim="${3:-1}"        # Default 1 IP
quota="${4:-0}"        # 0 means unlimited

# Server info
domain=$(cat /etc/xray/domain)
ISP=$(cat /etc/xray/isp)
CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid)
exp=$(date -d "$masaaktif days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"

# Check duplicate
if grep -q "\"$user\"" "$CONFIG_FILE"; then
    echo "❌ Error: Username '$user' sudah ada!"
    exit 1
fi

# Add to config
sed -i '/#vmess$/a\#vm '"$user $exp"'\
},{"id": "'"$uuid"'","alterId": "0","email": "'"$user"'"' "$CONFIG_FILE"
sed -i '/#vmessgrpc$/a\#vmg '"$user $exp"'\
},{"id": "'"$uuid"'","alterId": "0","email": "'"$user"'"' "$CONFIG_FILE"

# Generate links
vmess_ws_tls_json="{\"v\":\"2\",\"ps\":\"${user} TLS\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}"
vmess_ws_nontls_json="{\"v\":\"2\",\"ps\":\"${user} NTLS\",\"add\":\"${domain}\",\"port\":\"80\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"none\"}"
vmess_grpc_json="{\"v\":\"2\",\"ps\":\"${user} gRPC\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"grpc\",\"path\":\"vmess-grpc\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}"

vmesslink1="vmess://$(echo -n "$vmess_ws_tls_json" | base64 -w 0)"
vmesslink2="vmess://$(echo -n "$vmess_ws_nontls_json" | base64 -w 0)"
vmesslink3="vmess://$(echo -n "$vmess_grpc_json" | base64 -w 0)"

# Restart service
systemctl restart xray > /dev/null 2>&1

# Display values
[ "$iplim" = "0" ] && iplim_display="∞ Unlimited" || iplim_display="$iplim"
[ "$quota" = "0" ] && quota_display="∞ Unlimited" || quota_display="${quota} GB"

# Beautiful Format for Telegram (without HTML)
TEXT="
═══════[ PREMIUM VMESS ]═══════
🆔 Username: $user
🌐 Domain: $domain
⏳ Expired: $exp
═══════════════════════════════
📡 Server Info:
├─ 🏢 ISP: $ISP
└─ 🌆 City: $CITY
🔒 Security:
├─ 🔑 UUID: $uuid
└─ 🛡️ AlterID: 0
📊 Limits:
├─ 🖥️ IP Limit: $iplim_display
└─ 📶 Quota: $quota_display
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
⚠️ Gunakan sebelum expired!
"

# Save log
LOG_DIR="/etc/vmess/akun"
mkdir -p "$LOG_DIR"
echo "$TEXT" > "${LOG_DIR}/vmess-${user}.log"

# Output
echo "$TEXT"
