#!/bin/bash

# ==================================================================
#         SKRIP FINAL v10.0 - TROJAN (Replikasi Sempurna)
# ==================================================================

# --- Fungsi HTML Escape untuk Bash ---
# Melindungi karakter HTML spesial dari input agar tidak merusak formatting
html_escape() {
    local s="$1"
    s="${s//&/&amp;}" # Harus pertama
    s="${s//</&lt;}"
    s="${s//>/&gt;}"
    s="${s//\"/&quot;}"
    s="${s//\'/&#x27;}"
    echo "$s"
}
# --- Akhir Fungsi HTML Escape ---

# Validasi argumen
if [ "$#" -ne 4 ]; then
    echo "❌ Error: Butuh 4 argumen: &lt;user&gt; &lt;masa_aktif&gt; &lt;ip_limit&gt; &lt;kuota_gb&gt;" # Di-escape di sini
    exit 1
fi

# Ambil parameter
user="$1"; masaaktif="$2"; iplim="$3"; Quota="$4"

# Ambil variabel server
domain=$(cat /etc/xray/domain); ISP=$(cat /etc/xray/isp); CITY=$(cat /etc/xray/city)
uuid=$(cat /proc/sys/kernel/random/uuid); exp=$(date -d "$masaaktif days" +"%Y-%m-%d")
CONFIG_FILE="/etc/xray/config.json"

# Cek user (pastikan output ini juga HTML-safe)
if grep -q "\"$user\"" "$CONFIG_FILE"; then
    echo "❌ Error: Username '<b>$(html_escape "$user")</b>' sudah ada."
    exit 1
fi

# ==================================================================
#   Inti Perbaikan Final: Perintah 'sed' sekarang 100% identik.
# ==================================================================
# Tambahkan user ke Trojan WS
sed -i '/#trojanws$/a\#tr '"$(html_escape "$user") $exp $uuid"'\
},{"password": "'""$uuid""'","email": "'""$(html_escape "$user")""'"' "$CONFIG_FILE"

# Tambahkan user ke Trojan gRPC
sed -i '/#trojangrpc$/a\#trg '"$(html_escape "$user") $exp"'\
},{"password": "'""$uuid""'","email": "'""$(html_escape "$user")""'"' "$CONFIG_FILE"


# Atur variabel untuk output
if [ "$iplim" = "0" ]; then iplim_val="Unlimited"; else iplim_val="$(html_escape "$iplim")"; fi
if [ "$Quota" = "0" ]; then QuotaGb="Unlimited"; else QuotaGb="$(html_escape "$Quota")"; fi

# Buat link Trojan (URL sudah di-encode secara alami oleh protokol trojan://)
# Pastikan domain dan UUID di-escape jika ada kemungkinan karakter spesial
escaped_user=$(html_escape "$user")
escaped_domain=$(html_escape "$domain")
escaped_uuid=$(html_escape "$uuid")

trojanlink1="trojan://${escaped_uuid}@${escaped_domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni=${escaped_domain}#${escaped_user}"
trojanlink2="trojan://${escaped_uuid}@${escaped_domain}:443?path=%2Ftrojan-ws&security=tls&host=${escaped_domain}&type=ws&sni=${escaped_domain}#${escaped_user}"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# Hasilkan output lengkap untuk Telegram dengan ikon dan format keren
TEXT="
🌟━━━━━━━━━━━━━━━━━━🌟
<b>👑 Premium Trojan Account 👑</b>
🌟━━━━━━━━━━━━━━━━━━🌟
<b>👤 User</b>        : <code>${escaped_user}</code>
<b>🌐 Domain</b>      : <code>${escaped_domain}</code>
<b>🔒 Login Limit</b> : ${iplim_val} IP
<b>📊 Quota Limit</b> : ${QuotaGb} GB
<b>📡 ISP</b>         : ${escaped_ISP}
<b>🏙️ CITY</b>        : ${escaped_CITY}
<b>🔌 Port TLS</b>    : <code>443</code>
<b>🔌 Port GRPC</b>   : <code>443</code>
<b>🔑 Password</b>    : <code>${escaped_uuid}</code>
<b>🔗 Network</b>     : WS or gRPC
<b>➡️ Path WS</b>     : <code>/trojan-ws</code>
<b>➡️ ServiceName</b> : <code>trojan-grpc</code>
🌟━━━━━━━━━━━━━━━━━━🌟
<b>🔗 Link WS</b>     :
<pre>${trojanlink2}</pre>
🌟━━━━━━━━━━━━━━━━━━🌟
<b>🔗 Link GRPC</b>   :
<pre>${trojanlink1}</pre>
🌟━━━━━━━━━━━━━━━━━━🌟
<b>📅 Expired Until</b> : <code>$exp</code>
🌟━━━━━━━━━━━━━━━━━━🌟
"
echo "$TEXT"

# Membuat file log untuk user (tidak perlu HTML escaping di sini karena ini file log)
LOG_DIR="/etc/trojan/akun"
LOG_FILE="${LOG_DIR}/log-create-${user}.log"
mkdir -p "$LOG_DIR"
echo "◇━━━━━━━━━━━━━━━━━◇" > "$LOG_FILE"
echo "• Premium Trojan Account •" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"
echo "User         : ${user}" >> "$LOG_FILE"
echo "Domain       : ${domain}" >> "$LOG_FILE"
echo "Password/UUID: ${uuid}" >> "$LOG_FILE"
echo "Expired Until : $exp" >> "$LOG_FILE"
echo "Login Limit  : ${iplim_val}" >> "$LOG_FILE"
echo "Quota Limit  : ${QuotaGb}" >> "$LOG_FILE"
echo "Link WS      : ${trojanlink2}" >> "$LOG_FILE"
echo "Link GRPC    : ${trojanlink1}" >> "$LOG_FILE"
echo "◇━━━━━━━━━━━━━━━━━◇" >> "$LOG_FILE"

exit 0 # Pastikan script keluar dengan kode 0 untuk sukses
