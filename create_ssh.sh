#!/bin/bash

# =================================================================
#         Skrip Pembuatan Akun SSH untuk Hokage-BOT
# =================================================================
# Deskripsi: Skrip ini membuat user SSH, membuat file .txt di
# web server, dan menghasilkan output detail untuk bot Telegram.
# =================================================================

# --- Validasi Input ---
# Memeriksa apakah semua 4 argumen (input dari bot) diberikan
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

# --- Membuat User di Sistem ---
EXPIRED_DATE=$(date -d "+$DURATION days" +"%b %d, %Y") # Format tanggal: Jul 21, 2025
useradd -e "$(date -d "+$DURATION days" +"%Y-%m-%d")" -s /bin/false -M "$USERNAME"
echo -e "$PASSWORD\n$PASSWORD\n" | passwd "$USERNAME" &> /dev/null

# --- Mengambil Informasi Server ---
# Menggunakan '|| echo "..."' sebagai fallback jika file tidak ada
domain=$(cat /etc/xray/domain 2>/dev/null || echo "tidak_diatur")
sldomain=$(cat /etc/xray/dns 2>/dev/null || echo "tidak_diatur")
slkey=$(cat /etc/slowdns/server.pub 2>/dev/null || echo "tidak_diatur")
ISP=$(cat /etc/xray/isp 2>/dev/null || echo "tidak_diatur")
CITY=$(cat /etc/xray/city 2>/dev/null || echo "tidak_diatur")

# --- Membuat File .txt di Web Server ---
# Pastikan direktori /home/vps/public_html/ ada dan bisa ditulis
mkdir -p /home/vps/public_html/
cat > /home/vps/public_html/ssh-${USERNAME}.txt <<-END
_______________________________
Format SSH OVPN Account
_______________________________
Username         : $USERNAME
Password         : $PASSWORD
Expired          : $EXPIRED_DATE
_______________________________
Host             : $domain
ISP              : $ISP
CITY             : $CITY
Login Limit      : $IP_LIMIT IP
Port OpenSSH     : 22
Port Dropbear    : 143, 109
Port SSH WS      : 80, 8080
Port SSH SSL WS  : 443
Port SSL/TLS     : 8443, 8880
Port OVPN WS SSL : 2086
Port OVPN SSL    : 990
Port OVPN TCP    : 1194
Port OVPN UDP    : 2200
BadVPN UDP       : 7100, 7200, 7300
_______________________________
Host Slowdns    : $sldomain
Pub Key          : $slkey
_______________________________
OpenVPN Configs:
OVPN SSL         : http://$domain:89/ssl.ovpn
OVPN TCP         : http://$domain:89/tcp.ovpn
OVPN UDP         : http://$domain:89/udp.ovpn
_______________________________
END

# --- Menampilkan Output Lengkap untuk Bot Telegram ---
# Bot akan menangkap semua teks ini dan menampilkannya
cat << EOF
◇━━━━━━━━━━━━━━━━━◇
  • <b>SSH Premium Account</b> •
◇━━━━━━━━━━━━━━━━━◇
<b>Username</b>   : <code>$USERNAME</code>
<b>Password</b>   : <code>$PASSWORD</code>
<b>Expired On</b> : $EXPIRED_DATE
◇━━━━━━━━━━━━━━━━━◇
<b>ISP</b>          : $ISP
<b>City</b>         : $CITY
<b>Host</b>         : <code>$domain</code>
<b>Login Limit</b>  : $IP_LIMIT IP
<b>OpenSSH</b>      : 22
<b>Dropbear</b>     : 109, 143
<b>SSH-WS</b>       : 80, 8080
<b>SSH-SSL-WS</b>   : 443
<b>SSL/TLS</b>      : 8443, 8880
<b>OVPN TCP</b>     : http://$domain:89/tcp.ovpn
<b>OVPN UDP</b>     : http://$domain:89/udp.ovpn
<b>OVPN SSL</b>     : http://$domain:89/ssl.ovpn
<b>UDPGW</b>        : 7100-7300
◇━━━━━━━━━━━━━━━━━◇
<b>PORT SLOWDNS</b>: 80, 443, 53
<b>NAMESERVER</b> : <code>$sldomain</code>
<b>PUB KEY</b>      : <code>$slkey</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Payload WS/WSS:</b>
<code>GET / HTTP/1.1[crlf]Host: [host][crlf]Connection: Upgrade[crlf]User-Agent: [ua][crlf]Upgrade: ws[crlf][crlf]</code>
◇━━━━━━━━━━━━━━━━━◇
<b>Save Link Account</b>:
<code>http://$domain:89/ssh-$USERNAME.txt</code>
◇━━━━━━━━━━━━━━━━━◇
🙏 Terima kasih telah berbelanja vps ssh di Hokage Legend
  • HOKAGE LEGEND STORE •
◇━━━━━━━━━━━━━━━━━◇
EOF

# Mengakhiri skrip dengan status sukses
exit 0
