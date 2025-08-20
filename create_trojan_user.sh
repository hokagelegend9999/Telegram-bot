#!/bin/bash

# ==================================================================
#       SKRIP FINAL v10.0 - TROJAN (Versi Teks Biasa)
# ==================================================================

# Validasi argumen
if [ "$#" -ne 4 ]; then
    echo "❌ Error: Butuh 4 argumen: <user> <masa_aktif> <ip_limit> <kuota_gb>"
    exit 1
fi

# Ambil parameter
user="$1"; masaaktif="$2"; iplim="$3"; Quota="$4"

# Ambil variabel server
domain=$(cat /etc/xray/domain); ISP=$(cat /etc/xray/isp); CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid); exp=$(date -d "$masaaktif days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"

# Cek user
if grep -q "\"$user\"" "$CONFIG_FILE"; then
    echo "❌ Error: Username '$user' sudah ada."
    exit 1
fi

# ==================================================================
#   Inti Perbaikan Final: Perintah 'sed' sekarang 100% identik.
# ==================================================================
# Tambahkan user ke Trojan WS
sed -i '/#trojanws$/a\#tr '"$user $exp $uuid"'\
},{"password": "'""$uuid""'","email": "'""$user""'"' "$CONFIG_FILE"

# Tambahkan user ke Trojan gRPC
sed -i '/#trojangrpc$/a\#trg '"$user $exp"'\
},{"password": "'""$uuid""'","email": "'""$user""'"' "$CONFIG_FILE"


# Atur variabel untuk output
if [ "$Quota" = "0" ]; then QuotaGb="Unlimited"; else QuotaGb="$Quota"; fi
if [ "$iplim" = "0" ]; then iplim_val="Unlimited"; else iplim_val="$iplim"; fi

# Buat link Trojan
trojanlink1="trojan://${uuid}@${domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni=${domain}#${user}"
trojanlink2="trojan://${uuid}@${domain}:443?path=%2Ftrojan-ws&security=tls&host=${domain}&type=ws&sni=${domain}#${user}"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# Hasilkan output lengkap untuk Telegram dengan ikon dan format keren
TEXT="
🌟━━━━━━━━━━━━━━━━━━🌟
👑 Premium Trojan Account 👑
🌟━━━━━━━━━━━━━━━━━━🌟
👤 User        : ${user}
🌐 Domain      : ${domain}
🔒 Login Limit : ${iplim_val} IP
📊 Quota Limit : ${QuotaGb} GB
📡 ISP         : ${ISP}
🏙️ CITY        : ${CITY}
🔌 Port TLS    : 443
🔌 Port GRPC   : 443
🔑 Password    : ${uuid}
🔗 Network     : WS or gRPC
➡️ Path WS     : /trojan-ws
➡️ ServiceName : trojan-grpc
🌟━━━━━━━━━━━━━━━━━━🌟
🔗 Link WS     :
${trojanlink2}
🌟━━━━━━━━━━━━━━━━━━🌟
🔗 Link GRPC   :
${trojanlink1}
🌟━━━━━━━━━━━━━━━━━━🌟
📅 Expired Until : $exp
🌟━━━━━━━━━━━━━━━━━━🌟
"
echo "$TEXT"

# Membuat file log untuk user
LOG_DIR="/etc/trojan/akun"
LOG_FILE="${LOG_DIR}/log-create-${user}.log"
mkdir -p "$LOG_DIR"
echo "◇━━━━━━━━━━━━━━━━━◇" > "$LOG_FILE"
echo "• Premium Trojan Account •" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"
echo "User         : ${user}" >> "$LOG_FILE"
echo "Domain       : ${domain}" >> "$LOG_FILE"
echo "Password/UUID: ${uuid}" >> "$LOG_FILE"
echo "Expired Until: $exp" >> "$LOG_FILE"
echo "Login Limit  : ${iplim_val}" >> "$LOG_FILE"
echo "Quota Limit  : ${QuotaGb}" >> "$LOG_FILE"
echo "Link WS      : ${trojanlink2}" >> "$LOG_FILE"
echo "Link GRPC    : ${trojanlink1}" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"

exit 0
