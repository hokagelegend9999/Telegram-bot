#!/bin/bash

# ==================================================================
#         SKRIP FINAL v10.0 - TRIAL VMESS (Replikasi Sempurna)
# ==================================================================

TIMER_MINUTE="60"
TRIAL_LOG_FILE="/etc/hokage-bot/trial_users.log"

# Ambil variabel server
domain=$(cat /etc/xray/domain); ISP=$(cat /etc/xray/isp); CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid); exp=$(date -d "0 days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"

# Buat username acak
user="trial-$(tr -dc A-Z0-9 </dev/urandom | head -c 5)"

# Cek user agar tidak duplikat
if grep -q "\"$user\"" "$CONFIG_FILE"; then
    echo "Error: Gagal membuat username unik, silakan coba lagi."
    exit 1
fi

# ==================================================================
#    Inti Perbaikan Final: Perintah 'sed' sekarang 100% identik.
# ==================================================================
# Tambahkan user ke Vmess WS
sed -i '/#vmess$/a\#vm '"$user $exp"'\
},{"id": "'""$uuid""'","alterId": "0","email": "'""$user""'"' "$CONFIG_FILE"

# Tambahkan user ke Vmess gRPC
sed -i '/#vmessgrpc$/a\#vmg '"$user $exp"'\
},{"id": "'""$uuid""'","alterId": "0","email": "'""$user""'"' "$CONFIG_FILE"


# Mencatat user trial untuk dihapus oleh cron job
mkdir -p /etc/hokage-bot
EXP_TIME=$(date +%s -d "$TIMER_MINUTE minutes")
echo "${EXP_TIME}:${user}:vmess" >> "$TRIAL_LOG_FILE"

# Buat link Vmess
vmesslink1="vmess://$(echo -n "{\"v\":\"2\",\"ps\":\"${user}\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}" | base64 -w 0)"
vmesslink2="vmess://$(echo -n "{\"v\":\"2\",\"ps\":\"${user}\",\"add\":\"${domain}\",\"port\":\"80\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"none\"}" | base64 -w 0)"
vmesslink3="vmess://$(echo -n "{\"v\":\"2\",\"ps\":\"${user}\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"grpc\",\"path\":\"vmess-grpc\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}" | base64 -w 0)"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# Hasilkan output lengkap untuk Telegram
TEXT="
◇━━━━━━━━━━━━━━━━━◇
<b>Trial Premium Vmess Account</b>
◇━━━━━━━━━━━━━━━━━◇
<b>User</b>          : ${user}
<b>Domain</b>        : <code>${domain}</code>
<b>Expired On</b>      : $TIMER_MINUTE Minutes
<b>ISP</b>           : ${ISP}
<b>CITY</b>          : ${CITY}
<b>UUID</b>          : <code>${uuid}</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link TLS</b>      :
<code>${vmesslink1}</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link NTLS</b>     :
<code>${vmesslink2}</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link GRPC</b>     :
<code>${vmesslink3}</code>
◇━━━━━━━━━━━━━━━━━◇
"
echo "$TEXT"
