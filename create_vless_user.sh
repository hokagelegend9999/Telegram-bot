#!/bin/bash

# ==================================================================
#   SKRIP VLESS - Perbaikan Final dengan JQ (Metode Paling Aman)
# ==================================================================

# Validasi apakah jq sudah terinstall
if ! command -v jq &> /dev/null
then
    echo "❌ Error: 'jq' tidak ditemukan. Ini adalah alat penting untuk mengedit JSON dengan aman."
    echo "➡️  Silakan install terlebih dahulu dengan perintah: sudo apt update && sudo apt install jq -y"
    exit 1
fi

# Validasi argumen
if [ "$#" -ne 4 ]; then
    echo "❌ Error: Butuh 4 argumen: <user> <masa_aktif> <ip_limit> <kuota_gb>"
    exit 1
fi

# Ambil parameter
user="$1"
masaaktif="$2"
iplim="$3"
Quota="$4"

# Ambil variabel server
domain=$(cat /etc/xray/domain)
ISP=$(cat /etc/xray/isp)
CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid)
exp=$(date -d "$masaaktif days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"
TMP_FILE="/etc/xray/config.json.tmp" # File sementara untuk keamanan

# Cek duplikasi user menggunakan jq (lebih akurat)
if jq -e --arg user "$user" '.inbounds[].settings.clients[] | select(.email == $user)' "$CONFIG_FILE" > /dev/null; then
    echo "❌ Error: Username '$user' sudah ada."
    exit 1
fi

# ==================================================================
#   Inti Perbaikan: Menggunakan 'jq' untuk menambahkan user
#   Ini adalah cara yang benar dan tidak akan merusak sintaks JSON.
# ==================================================================
# Buat object client baru dalam format JSON
new_client_json="{\"id\": \"$uuid\", \"email\": \"$user\"}"

# Tambahkan user ke Vless WS (mencari inbound dengan path "/vless")
jq --argjson client "$new_client_json" '
    (.inbounds[] | select(.streamSettings.wsSettings.path == "/vless") .settings.clients) |= . + [$client]
' "$CONFIG_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CONFIG_FILE"

# Tambahkan user ke Vless gRPC (mencari inbound dengan serviceName "vless-grpc")
jq --argjson client "$new_client_json" '
    (.inbounds[] | select(.streamSettings.grpcSettings.serviceName == "vless-grpc") .settings.clients) |= . + [$client]
' "$CONFIG_FILE" > "$TMP_FILE" && mv "$TMP_FILE" "$CONFIG_FILE"

# Tambahkan baris komentar untuk logging manual Anda (ini aman)
sed -i '/#vless$/a\#vl '"$user $exp $uuid"'' "$CONFIG_FILE"
sed -i '/#vlessgrpc$/a\#vlg '"$user $exp $uuid"'' "$CONFIG_FILE"

# Atur variabel untuk output
if [ "$iplim" = "0" ]; then iplim_val="Unlimited"; else iplim_val="$iplim"; fi
if [ "$Quota" = "0" ]; then QuotaGb="Unlimited"; else QuotaGb="$Quota"; fi

# Buat link Vless
vlesslink1="vless://${uuid}@${domain}:443?path=/vless&security=tls&encryption=none&host=${domain}&type=ws&sni=${domain}#${user}"
vlesslink2="vless://${uuid}@${domain}:80?path=/vless&security=none&encryption=none&host=${domain}&type=ws#${user}"
vlesslink3="vless://${uuid}@${domain}:443?mode=gun&security=tls&encryption=none&type=grpc&serviceName=vless-grpc&sni=${domain}#${user}"

# Restart service xray dan lakukan pengecekan
systemctl restart xray
sleep 1
if ! systemctl is-active --quiet xray; then
    echo "🚨 Peringatan: Layanan Xray GAGAL direstart. Walaupun sudah menggunakan jq, mungkin ada masalah lain."
    echo "Silakan periksa file config dan log dengan 'journalctl -u xray -e'."
    exit 1
fi

# Hasilkan output lengkap untuk Telegram
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

# Membuat file log untuk user
LOG_DIR="/etc/vless/akun"
LOG_FILE="${LOG_DIR}/log-create-${user}.log"
mkdir -p "$LOG_DIR"
echo "◇━━━━━━━━━━━━━━━━━◇" > "$LOG_FILE"
echo "• Premium Vless Account •" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"
echo "User          : ${user}" >> "$LOG_FILE"
echo "Domain        : ${domain}" >> "$LOG_FILE"
echo "UUID          : ${uuid}" >> "$LOG_FILE"
echo "Expired Until : $exp" >> "$LOG_FILE"
echo "Login Limit   : ${iplim_val}" >> "$LOG_FILE"
echo "Quota Limit   : ${QuotaGb}" >> "$LOG_FILE"
echo "Link TLS      : ${vlesslink1}" >> "$LOG_FILE"
echo "Link NTLS     : ${vlesslink2}" >> "$LOG_FILE"
echo "Link GRPC     : ${vlesslink3}" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"

exit 0
