#!/bin/bash

# ==================================================================
#               SKRIP FINAL v9.0 - Replikasi Sempurna
# ==================================================================

# Validasi argumen
if [ "$#" -ne 4 ]; then
    echo "Error: Butuh 4 argumen: <user> <masa_aktif> <ip_limit> <kuota_gb>"
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
    echo "Error: Username '$user' sudah ada."
    exit 1
fi

# ==================================================================
#    Inti Perbaikan: Perintah 'sed' sekarang 100% sama dengan skrip asli Anda.
# ==================================================================
# Tambahkan user ke Vmess WS
sed -i '/#vmess$/a\#vm '"$user $exp"'\
},{"id": "'""$uuid""'","alterId": "0","email": "'""$user""'"' "$CONFIG_FILE"

# Tambahkan user ke Vmess gRPC
sed -i '/#vmessgrpc$/a\#vmg '"$user $exp"'\
},{"id": "'""$uuid""'","alterId": "0","email": "'""$user""'"' "$CONFIG_FILE"


# Atur variabel untuk output
if [ "$iplim" = "0" ]; then iplim_val="Unlimited"; else iplim_val="$iplim"; fi
if [ "$Quota" = "0" ]; then QuotaGb="Unlimited"; else QuotaGb="$Quota"; fi

# Buat link Vmess
vmess_ws_tls_json="{\"v\":\"2\",\"ps\":\"${user}\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}"
vmess_ws_nontls_json="{\"v\":\"2\",\"ps\":\"${user}\",\"add\":\"${domain}\",\"port\":\"80\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"ws\",\"path\":\"/vmess\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"none\"}"
vmess_grpc_json="{\"v\":\"2\",\"ps\":\"${user}\",\"add\":\"${domain}\",\"port\":\"443\",\"id\":\"${uuid}\",\"aid\":\"0\",\"net\":\"grpc\",\"path\":\"vmess-grpc\",\"type\":\"none\",\"host\":\"${domain}\",\"tls\":\"tls\"}"
vmesslink1="vmess://$(echo -n "$vmess_ws_tls_json" | base64 -w 0)"
vmesslink2="vmess://$(echo -n "$vmess_ws_nontls_json" | base64 -w 0)"
vmesslink3="vmess://$(echo -n "$vmess_grpc_json" | base64 -w 0)"

# Restart service xray
systemctl restart xray > /dev/null 2>&1

# Hasilkan output lengkap untuk Telegram
TEXT="
◇━━━━━━━━━━━━━━━━━◇
<b>Premium Vmess Account</b>
◇━━━━━━━━━━━━━━━━━◇
<b>User</b>          : ${user}
<b>Domain</b>        : <code>${domain}</code>
<b>Login Limit</b>   : ${iplim_val} IP
<b>Quota Limit</b>   : ${QuotaGb} GB
<b>ISP</b>           : ${ISP}
<b>CITY</b>          : ${CITY}
<b>Port TLS</b>      : 443
<b>Port NTLS</b>     : 80, 8080
<b>Port GRPC</b>     : 443
<b>UUID</b>          : <code>${uuid}</code>
<b>AlterId</b>       : 0
<b>Security</b>      : auto
<b>Network</b>       : WS or gRPC
<b>Path</b>          : <code>/vmess</code>
<b>ServiceName</b>   : <code>vmess-grpc</code>
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
<b>Expired Until</b> : $exp
◇━━━━━━━━━━━━━━━━━◇
"
