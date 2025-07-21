#!/bin/bash

# ==================================================================
#         SKRIP FINAL v9.1 - VLESS (Replikasi Sempurna)
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
#   Inti Perbaikan: Perintah 'sed' sekarang 100% sama dengan skrip asli Anda.
# ==================================================================
# Tambahkan user ke Vless WS
sed -i '/#vless$/a\#vl '"$user $exp $uuid"'\
},{"id": "'""$uuid""'","email": "'""$user""'"}' "$CONFIG_FILE"

# Tambahkan user ke Vless gRPC
sed -i '/#vlessgrpc$/a\#vlg '"$user $exp"'\
},{"id": "'""$uuid""'","email": "'""$user""'"}' "$CONFIG_FILE"


# Atur variabel untuk output
if [ "$iplim" = "0" ]; then iplim_val="Unlimited"; else iplim_val="$iplim"; fi
if [ "$Quota" = "0" ]; then QuotaGb="Unlimited"; else QuotaGb="$Quota"; fi

# Buat link Vless (linknya tetap valid, hanya tampilannya yang plain text)
vlesslink1="vless://${uuid}@${domain}:443?path=/vless&security=tls&encryption=none&host=${domain}&type=ws&sni=${domain}#${user}"
vlesslink2="vless://${uuid}@${domain}:80?path=/vless&security=none&encryption=none&host=${domain}&type=ws#${user}"
vlesslink3="vless://${uuid}@${domain}:443?mode=gun&security=tls&encryption=none&type=grpc&serviceName=vless-grpc&sni=${domain}#${user}"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# Hasilkan output lengkap untuk Telegram (Plain Text dengan Emoji)
TEXT="
◇━━━━━━━━━━━━━━━━━◇
👑 Premium Vless Account 👑
◇━━━━━━━━━━━━━━━━━◇
👤 User        : ${user}
🌐 Domain      : ${domain}
🔒 Login Limit : ${iplim_val} IP
📊 Quota Limit : ${QuotaGb} GB
📡 ISP         : ${ISP}
🏙️ CITY        : ${CITY}
🔌 Port TLS    : 443
🔌 Port NTLS   : 80, 8080
🔌 Port GRPC   : 443
🔑 UUID        : ${uuid}
🔗 Encryption  : none
🔗 Network     : WS or gRPC
➡️ Path        : /vless
➡️ ServiceName : vless-grpc
◇━━━━━━━━━━━━━━━━━◇
🔗 Link TLS    :
${vlesslink1}
◇━━━━━━━━━━━━━━━━━◇
🔗 Link NTLS   :
${vlesslink2}
◇━━━━━━━━━━━━━━━━━◇
🔗 Link GRPC   :
${vlesslink3}
◇━━━━━━━━━━━━━━━━━◇
📅 Expired Until : $exp
◇━━━━━━━━━━━━━━━━━◇
"
echo "$TEXT"

# Membuat file log untuk user (tidak perlu HTML escaping di sini karena ini file log)
LOG_DIR="/etc/vless/akun"
LOG_FILE="${LOG_DIR}/log-create-${user}.log"
mkdir -p "$LOG_DIR"
echo "◇━━━━━━━━━━━━━━━━━◇" > "$LOG_FILE"
echo "• Premium Vless Account •" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"
echo "User         : ${user}" >> "$LOG_FILE"
echo "Domain       : ${domain}" >> "$LOG_FILE"
echo "UUID         : ${uuid}" >> "$LOG_FILE"
echo "Expired Until : $exp" >> "$LOG_FILE"
echo "Login Limit  : ${iplim_val}" >> "$LOG_FILE"
echo "Quota Limit  : ${QuotaGb}" >> "$LOG_FILE"
echo "Link TLS     : ${vlesslink1}" >> "$LOG_FILE"
echo "Link NTLS    : ${vlesslink2}" >> "$LOG_FILE"
echo "Link GRPC    : ${vlesslink3}" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"

exit 0
