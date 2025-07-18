#!/bin/bash
set -e # Pastikan skrip berhenti jika ada error

# ==================================================================
#         SKRIP FINAL v12.1 - TRIAL TROJAN (Output Stabil)
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
if grep -q -w "$user" "$CONFIG_FILE"; then
    echo "Error: Gagal membuat username unik, silakan coba lagi."
    exit 1
fi

# Perintah 'sed' yang sudah 100% benar
sed -i '/#trojanws$/a\#tr '"$user $exp $uuid"'\
},{"password": "'""$uuid""'","email": "'""$user""'"' "$CONFIG_FILE"
sed -i '/#trojangrpc$/a\#trg '"$user $exp"'\
},{"password": "'""$uuid""'","email": "'""$user""'"' "$CONFIG_FILE"

# Mencatat user trial untuk dihapus oleh cron job
mkdir -p /etc/hokage-bot
EXP_TIME=$(date +%s -d "$TIMER_MINUTE minutes")
echo "${EXP_TIME}:${user}:trojan" >> "$TRIAL_LOG_FILE"

# Buat link Trojan
trojanlink1="trojan://${uuid}@${domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni=${domain}#${user}"
trojanlink2="trojan://${uuid}@${domain}:443?path=%2Ftrojan-ws&security=tls&host=${domain}&type=ws&sni=${domain}#${user}"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# ==================================================================
#    Inti Perbaikan: Menggunakan Here Document (cat <<EOF)
# ==================================================================
TEXT=$(cat <<EOF
◇━━━━━━━━━━━━━━━━━◇
<b>Trial Premium Trojan Account</b>
◇━━━━━━━━━━━━━━━━━◇
<b>User</b>          : ${user}
<b>Domain</b>        : <code>${domain}</code>
<b>Expired On</b>      : ${TIMER_MINUTE} Minutes
<b>Password</b>      : <code>${uuid}</code>
<b>ISP</b>           : ${ISP}
<b>CITY</b>          : ${CITY}
<b>Path WS</b>       : <code>/trojan-ws</code>
<b>ServiceName</b>   : <code>trojan-grpc</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link WS</b>       :
<code>${trojanlink2}</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Link GRPC</b>     :
<code>${trojanlink1}</code>
◇━━━━━━━━━━━━━━━━━◇
EOF
)
echo "$TEXT"

# Membuat file log untuk user
LOG_DIR="/etc/trojan/akun"
LOG_FILE="${LOG_DIR}/log-create-${user}.log"
mkdir -p "$LOG_DIR"
cat <<EOF > "$LOG_FILE"
◇━━━━━━━━━━━━━━━━━◇
• Trial Premium Trojan Account •
◇━━━━━━━━━━━━━━━━━◇
User         : ${user}
Domain       : ${domain}
Password/UUID: ${uuid}
Expired Until  : ${TIMER_MINUTE} Minutes
◇━━━━━━━━━━━━━━━━━◇
EOF
