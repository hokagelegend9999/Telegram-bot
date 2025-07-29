#!/bin/bash

# =================================================================
#           Skrip Pembuatan Akun SSH untuk Hokage-BOT
#           Versi Final: Diperbaiki & Disederhanakan
# =================================================================

# --- Validasi Input ---
if [ "$#" -ne 4 ]; then
    echo "Error: Input tidak lengkap."
    echo "Penggunaan: $0 <username> <password> <durasi_hari> <limit_ip>"
    exit 1
fi

# --- Inisialisasi Variabel ---
USERNAME=$1
PASSWORD=$2
DURATION=$3
IP_LIMIT=$4
EXPIRED_DATE=$(date -d "+$DURATION days" +"%b %d, %Y")
EXPIRED_UNIX=$(date -d "+$DURATION days" +"%Y-%m-%d")

# --- Membuat User di Sistem dengan Penanganan Error ---
if id "$USERNAME" &>/dev/null; then
    echo "Error: User '$USERNAME' sudah ada."
    exit 1
fi

useradd -e "$EXPIRED_UNIX" -s /bin/false -M "$USERNAME"
if [ $? -ne 0 ]; then
    echo "Error: Gagal membuat user '$USERNAME'."
    exit 1
fi
echo -e "$PASSWORD\n$PASSWORD\n" | passwd "$USERNAME" &> /dev/null

# --- Mengambil Informasi Server ---
domain=$(cat /etc/xray/domain 2>/dev/null || echo "not_set")
sldomain=$(cat /etc/xray/dns 2>/dev/null || echo "not_set")
slkey=$(cat /etc/slowdns/server.pub 2>/dev/null || echo "not_set")
ISP=$(cat /etc/xray/isp 2>/dev/null || echo "Unknown")
CITY=$(cat /etc/xray/city 2>/dev/null || echo "Unknown")

# --- Membuat File .txt di Web Server ---
mkdir -p /home/vps/public_html/
cat > /home/vps/public_html/ssh-${USERNAME}.txt <<-END
SSH & OpenVPN Account Details
===============================
Username        : $USERNAME
Password        : $PASSWORD
Expired On      : $EXPIRED_DATE
-------------------------------
Host / Server   : $domain
ISP             : $ISP
City            : $CITY
Login Limit     : $IP_LIMIT IP
-------------------------------
Port Details:
- OpenSSH       : 22
- Dropbear      : 143, 109
- SSH WS        : 80, 8080
- SSH SSL WS    : 443
- SSL/TLS       : 8443, 8880
- OVPN WS SSL   : 2086
- OVPN SSL      : 990
- OVPN TCP      : 1194
- OVPN UDP      : 2200
- BadVPN UDP    : 7100, 7200, 7300
-------------------------------
SlowDNS Details:
- Host SlowDNS  : $sldomain
- Public Key    : $slkey
-------------------------------
OpenVPN Configs:
- OVPN SSL      : http://$domain:89/ssl.ovpn
- OVPN TCP      : http://$domain:89/tcp.ovpn
- OVPN UDP      : http://$domain:89/udp.ovpn
===============================
END

# =======================================================
# PENAMBAHAN FITUR: Simpan data user ke /etc/xray/ssh
# =======================================================
echo "### $USERNAME $PASSWORD $EXPIRED_DATE" >> /etc/xray/ssh
# =======================================================

# --- Menampilkan Output Lengkap untuk Bot Telegram (Dipercantik) ---
cat << EOF
🎊 SSH Premium Account Created 🎊
━━━━━━━━━━━━━━━━━━━━━━━━━━
📄 Account Info
  ┣ Username   : ${USERNAME}
  ┣ Password   : ${PASSWORD}
  ┣ Host       : ${domain}
  ┗ Expired On : ${EXPIRED_DATE}
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔌 Connection Info
  ┣ ISP        : ${ISP}
  ┣ City       : ${CITY}
  ┣ Limit      : ${IP_LIMIT} Device(s)
  ┣ OpenSSH    : 22
  ┣ Dropbear   : 109, 143
  ┣ SSL/TLS    : 8443, 8880
  ┣ SSH WS     : 80, 8080
  ┣ SSH SSL WS : 443
  ┗ UDPGW      : 7100-7300
━━━━━━━━━━━━━━━━━━━━━━━━━━
🔗 Links & Payloads
  ┣ OVPN TCP : http://${domain}:89/tcp.ovpn
  ┣ OVPN UDP : http://${domain}:89/udp.ovpn
  ┗ OVPN SSL : http://${domain}:89/ssl.ovpn
  
  📋 Payload WS/WSS:
  GET / HTTP/1.1[crlf]Host: ${domain}[crlf]Upgrade: websocket[crlf]Connection: upgrade[crlf][crlf]
━━━━━━━━━━━━━━━━━━━━━━━━━━
SlowDNS Nameserver & Key
  ┣ NS    : ${sldomain}
  ┗ Key   : ${slkey}
━━━━━━━━━━━━━━━━━━━━━━━━━━
💾 Save Full Config:
http://${domain}:89/ssh-${USERNAME}.txt
━━━━━━━━━━━━━━━━━━━━━━━━━━
🙏 Terima kasih telah order di Hokage Legend
EOF

# Mengakhiri skrip dengan status sukses
exit 0
