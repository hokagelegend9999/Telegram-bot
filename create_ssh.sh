#!/bin/bash

# Pastikan script dijalankan sebagai root
if [ "$(id -u)" -ne 0 ]; then
   echo "{\"error\": \"This script must be run as root\"}"
   exit 1
fi

# Argumen: 1=Username, 2=Masa Aktif (hari), 3=Password
USERNAME=$1
MASA_AKTIF=$2
PASSWORD=$3

# Validasi input
if [ -z "$USERNAME" ] || [ -z "$MASA_AKTIF" ] || [ -z "$PASSWORD" ]; then
  echo "{\"error\": \"Username, Masa Aktif, dan Password diperlukan.\"}"
  exit 1
fi

# Cek jika user sudah ada
if id "$USERNAME" &>/dev/null; then
    echo "{\"error\": \"Username '$USERNAME' sudah ada.\"}"
    exit 1
fi

# --- Pengumpulan Data dari Sistem ---
MYIP=$(wget -qO- ipv4.icanhazip.com);
if [ -f /etc/xray/domain ]; then
    DOMEN=$(cat /etc/xray/domain)
elif [ -f /etc/v2ray/domain ]; then
    DOMEN=$(cat /etc/v2ray/domain)
else
    DOMEN=$MYIP
fi
PORT_OPENSSH=$(grep -w "OpenSSH" /root/log-install.txt | cut -d: -f2 | awk '{print $1}')
PORT_SSH_WS=$(grep -w "SSH Websocket" /root/log-install.txt | cut -d: -f2 | awk '{print $1}')
PORT_SSH_SSL_WS=$(grep -w "SSH SSL Websocket" /root/log-install.txt | cut -d: -f2 | awk '{print $1}')
PORT_STUNNEL=$(grep -w "Stunnel4" /root/log-install.txt | cut -d: -f2 | xargs)
PORT_SQUID=$(grep -w "Squid Proxy" /root/log-install.txt | cut -d: -f2 | xargs)
NS_DOMAIN=$(cat /root/nsdomain)
NS_PUBKEY=$(cat /etc/slowdns/server.pub)
OVPN_TCP_PORT="1194"
OVPN_UDP_PORT="2200"
OVPN_TCP_LINK="http://$MYIP:81/client-tcp-$OVPN_TCP_PORT.ovpn"
OVPN_UDP_LINK="http://$MYIP:81/client-udp-$OVPN_UDP_PORT.ovpn"
PAYLOAD_WS="GET / HTTP/1.1[crlf]Host: $DOMEN[crlf]Upgrade: websocket[crlf][crlf]"
PAYLOAD_WSS="GET wss://your_bug_host HTTP/1.1[crlf]Host: $DOMEN[crlf]Upgrade: websocket[crlf][crlf]"

# --- Proses Pembuatan User ---
EXP_DATE=$(date -d "$MASA_AKTIF days" +"%Y-%m-%d")
useradd -e "$EXP_DATE" -s /bin/false -M "$USERNAME"
echo -e "$PASSWORD\n$PASSWORD\n" | passwd "$USERNAME" &> /dev/null
EXP_DATE_FORMAT=$(chage -l "$USERNAME" | grep "Account expires" | awk -F": " '{print $2}')

# --- BLOK LOGGING BARU ---
# Blok ini akan menulis ke file log tanpa mengganggu output JSON
(
cat <<LOG_EOF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             SSH Account             
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Username     : $USERNAME
Password     : $PASSWORD
Expired On   : $EXP_DATE_FORMAT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IP           : $MYIP
Host         : $DOMEN
OpenSSH      : $PORT_OPENSSH
SSH WS       : $PORT_SSH_WS
SSH SSL WS   : $PORT_SSH_SSL_WS
SSL/TLS      : $PORT_STUNNEL
UDPGW        : 7100-7900
Nameserver   : $NS_DOMAIN
Pubkey       : $NS_PUBKEY
Squid Proxy  : $PORT_SQUID
OpenVPN TCP  : $OVPN_TCP_LINK
OpenVPN UDP  : $OVPN_UDP_LINK
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

LOG_EOF
) | tee -a /etc/log-create-ssh.log > /dev/null
# --- AKHIR BLOK LOGGING ---


# --- Hasilkan Output JSON untuk Bot ---
cat <<EOF
{
  "status": "success",
  "username": "$USERNAME",
  "password": "$PASSWORD",
  "expires_on": "$EXP_DATE_FORMAT",
  "ip_address": "$MYIP",
  "host": "$DOMEN",
  "port_openssh": "$PORT_OPENSSH",
  "port_ssh_ws": "$PORT_SSH_WS",
  "port_ssh_ssl_ws": "$PORT_SSH_SSL_WS",
  "port_stunnel": "$PORT_STUNNEL",
  "port_squid": "$PORT_SQUID",
  "port_udpgw": "7100-7900",
  "ns_domain": "$NS_DOMAIN",
  "ns_pubkey": "$NS_PUBKEY",
  "ovpn_tcp_link": "$OVPN_TCP_LINK",
  "ovpn_udp_link": "$OVPN_UDP_LINK",
  "payload_ws": "$PAYLOAD_WS",
  "payload_wss": "$PAYLOAD_WSS"
}
EOF
