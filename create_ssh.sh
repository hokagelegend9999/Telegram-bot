#!/bin/bash

# Validasi bahwa 4 argumen diberikan (username, password, masaaktif, iplim)
if [ "$#" -ne 4 ]; then
    # Jika argumen tidak cukup, keluar dengan pesan error (untuk debugging)
    echo "Error: Butuh 4 argumen: <username> <password> <masa_aktif> <ip_limit>"
    exit 1
fi

# Ambil parameter dari argumen
Login="$1"
Pass="$2"
masaaktif="$3"
iplim="$4"

# Ambil variabel lingkungan dari server
domen=$(cat /etc/xray/domain)
sldomain=$(cat /etc/xray/dns)
slkey=$(cat /etc/slowdns/server.pub)
ISP=$(cat /etc/xray/isp)
CITY=$(cat /etc/xray/city)

# Cek apakah user sudah ada
CLIENT_EXISTS=$(id -u "$Login" >/dev/null 2>&1; echo $?)
if [ "$CLIENT_EXISTS" -eq 0 ]; then
    echo "Error: Username '$Login' sudah ada di sistem."
    exit 1
fi

# Proses pembuatan user
expi=$(date -d "$masaaktif days" +"%Y-%m-%d")
useradd -e "$expi" -s /bin/false -M "$Login"
echo -e "$Pass\n$Pass\n" | passwd "$Login" > /dev/null 2>&1
exp="$(chage -l "$Login" | grep "Account expires" | awk -F": " '{print $2}')"

# Simpan data user
echo "### $Login $expi $Pass" >> /etc/xray/ssh
mkdir -p /etc/xray/sshx
echo "${iplim}" > "/etc/xray/sshx/${Login}IP"

# Hasilkan output yang akan dikirim ke bot
# Format ini SAMA PERSIS dengan yang Anda inginkan
TEXT="
◇━━━━━━━━━━━━━━━━━◇
SSH Premium Account
◇━━━━━━━━━━━━━━━━━◇
Username        : $Login
Password        : $Pass
Expired On      : $exp
◇━━━━━━━━━━━━━━━━━◇
ISP             : $ISP
CITY            : $CITY
Host            : $domen
Login Limit     : ${iplim} IP
Port OpenSSH    : 22
Port Dropbear   : 109, 143
Port SSH WS     : 80, 8080
Port SSH SSL WS : 443
Port SSL/TLS    : 8443, 8880
Port OVPN WS SSL: 2086
Port OVPN SSL   : 990
Port OVPN TCP   : 1194
Port OVPN UDP   : 2200
Proxy Squid     : 3128
BadVPN UDP      : 7100, 7200, 7300
◇━━━━━━━━━━━━━━━━━◇
SSH UDP VIRAL : $domen:1-65535@$Login:$Pass
◇━━━━━━━━━━━━━━━━━◇
HTTP CUSTOM WS: $domen:80@$Login:$Pass
◇━━━━━━━━━━━━━━━━━◇
Host Slowdns    : $sldomain
Port Slowdns    : 80, 443, 53
Pub Key         : $slkey
◇━━━━━━━━━━━━━━━━━◇
Payload WS/WSS  :
GET / HTTP/1.1[crlf]Host: [host][crlf]Connection: Upgrade[crlf]User-Agent: [ua][crlf]Upgrade: ws[crlf][crlf]
◇━━━━━━━━━━━━━━━━━◇
OpenVPN SSL     : http://$domen:89/ssl.ovpn
OpenVPN TCP     : http://$domen:89/tcp.ovpn
OpenVPN UDP     : http://$domen:89/udp.ovpn
◇━━━━━━━━━━━━━━━━━◇
Save Link Account: http://$domen:89/ssh-$Login.txt
◇━━━━━━━━━━━━━━━━━◇
"
# Cetak output ke stdout agar bisa ditangkap oleh Python
echo "$TEXT"
```
