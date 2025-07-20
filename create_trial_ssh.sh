#!/bin/bash

# =================================================================
#        Trial SSH Creator - Telegram Friendly Format
# =================================================================

# Configuration
TIMER_MINUTE="10"  # Trial duration in minutes

# System information
domain=$(cat /etc/xray/domain 2>/dev/null)
sldomain=$(cat /etc/xray/dns 2>/dev/null)
slkey=$(cat /etc/slowdns/server.pub 2>/dev/null)
ISP=$(cat /etc/xray/isp 2>/dev/null)
CITY=$(cat /etc/xray/city 2>/dev/null)

# Account details
Login="Trial-$(tr -dc A-Z0-9 </dev/urandom | head -c 4)"
Pass="1"      # Default password
iplim="1"     # IP limit

# Create user
useradd -e "$(date -d "1 day" +"%Y-%m-%d")" -s /bin/false -M "$Login" || {
    echo "❌ Error: Gagal membuat user baru"
    exit 1
}

# Set password
echo -e "$Pass\n$Pass\n" | passwd "$Login" &> /dev/null
echo "### $Login $(date -d "1 day" +"%Y-%m-%d") $Pass" >> /etc/xray/ssh

# Schedule auto-deletion
(crontab -l 2>/dev/null; echo "*/$TIMER_MINUTE * * * * userdel -r $Login && rm -f /etc/cron.d/trialssh${Login}") | crontab -
mv /var/spool/cron/crontabs/root /etc/cron.d/trialssh${Login}
chmod 600 /etc/cron.d/trialssh${Login}

# Beautiful Telegram Format (without HTML)
TEXT="
═══════[ TRIAL SSH ]═══════
🆔 Username: $Login
🔑 Password: $Pass
⏳ Expired: $TIMER_MINUTE Minutes
═══════════════════════════════
🌐 Server Info:
├─ 🏢 ISP: $ISP
└─ 🌆 City: $CITY
📡 Connection:
├─ 🌍 Domain: $domain
└─ 🐌 SlowDNS: $sldomain
🔒 Security:
├─ 🛡️ IP Limit: $iplim
└─ ⚠️ Auto-delete after trial
═══════════════════════════════
🔌 Port Configuration:
┌─ 🔌 SSH: 22
├─ 🔌 Dropbear: 109, 143
├─ 🌐 WS: 80, 8080
├─ 🔐 SSL WS: 443
├─ 🔒 SSL/TLS: 8443, 8880
├─ 🛡️ OVPN WS: 2086
└─ 🌀 BadVPN: 7100-7300
═══════════════════════════════
📋 Payload WS:
GET / HTTP/1.1[crlf]
Host: $domain[crlf]
Connection: Upgrade[crlf]
User-Agent: [ua][crlf]
Upgrade: websocket[crlf][crlf]
═══════════════════════════════
⚠️ Trial akan expired setelah $TIMER_MINUTE menit!
"

# Output
echo "$TEXT"
exit 0
