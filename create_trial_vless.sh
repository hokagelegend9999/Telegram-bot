#!/bin/bash

# ==================================================================
#         SKRIP FINAL - TRIAL VLESS (Meniru Vmess Trial)
# ==================================================================

TIMER_MINUTE="60"
TRIAL_LOG_FILE="/etc/hokage-bot/trial_users.log"

# Ambil variabel server
domain=$(cat /etc/xray/domain); ISP=$(cat /etc/xray/isp); CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid); exp=$(date -d "0 days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"

# Buat username acak dan pastikan tidak duplikat
while true; do
    user="trial-$(tr -dc A-Z0-9 </dev/urandom | head -c 5)"
    if ! grep -q -w "$user" "$CONFIG_FILE"; then
        break
    fi
done

# Meniru persis perintah 'sed' dari skrip Vless biasa yang stabil
sed -i '/#vless$/a\#vl '"$user $exp $uuid"'\
,{"id": "'""$uuid""'","email": "'""$user""'"' "$CONFIG_FILE"
sed -i '/#vlessgrpc$/a\#vlg '"$user $exp"'\
,{"id": "'""$uuid""'","email": "'""$user""'"' "$CONFIG_FILE"

# Mencatat user trial untuk dihapus oleh cron job
mkdir -p /etc/hokage-bot
EXP_TIME=$(date +%s -d "$TIMER_MINUTE minutes")
echo "${EXP_TIME}:${user}:vless" >> "$TRIAL_LOG_FILE"

# Buat link Vless
vlesslink1="vless://${uuid}@${domain}:443?path=/vless&security=tls&encryption=none&host=${domain}&type=ws&sni=${domain}#${user}"
vlesslink2="vless://${uuid}@${domain}:80?path=/vless&security=none&encryption=none&host=${domain}&type=ws#${user}"
vlesslink3="vless://${uuid}@${domain}:443?mode=gun&security=tls&encryption=none&type=grpc&serviceName=vless-grpc&sni=${domain}#${user}"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# Hasilkan output lengkap untuk Telegram
TEXT="
◇━━━━━━━━━━━━━━━━━◇
<b>Trial Premium Vless Account</b>
◇━━━━━━━━━━━━━━━━━◇
<b>User</b>          : ${user}
<b>Domain</b>        : <code>${domain}</code>
<b>Expired On</b>      : $TIMER_MINUTE Minutes
<b>ISP</b>           : ${ISP}
<b>CITY</b>          : ${CITY}
<b>UUID</b>          : <code>${uuid}</code>
<b>Path</b>          : <code>/vless</code>
<b>ServiceName</b>   : <code>vless-grpc</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link TLS</b>      :
<code>${vlesslink1}</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link NTLS</b>     :
<code>${vlesslink2}</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link GRPC</b>     :
<code>${vlesslink3}</code>
◇━━━━━━━━━━━━━━━━━◇
"
echo "$TEXT"

# Membuat file log untuk user
LOG_DIR="/etc/vless/akun"
LOG_FILE="${LOG_DIR}/log-create-${user}.log"
mkdir -p "$LOG_DIR"
echo "◇━━━━━━━━━━━━━━━━━◇" > "$LOG_FILE"
echo "• Trial Premium Vless Account •" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"
echo "User         : ${user}" >> "$LOG_FILE"
echo "Domain       : ${domain}" >> "$LOG_FILE"
echo "UUID         : ${uuid}" >> "$LOG_FILE"
echo "Expired Until  : ${TIMER_MINUTE} Minutes" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"
