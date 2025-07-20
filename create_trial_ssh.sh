#!/bin/bash

# ====================================================
#        SSH Trial Account Creator
# ====================================================

TIMER_MINUTE="60"
TRIAL_LOG_FILE="/etc/hokage-bot/trial_users.log"

# Server info
domain=$(cat /etc/xray/domain 2>/dev/null)
sldomain=$(cat /etc/xray/dns 2>/dev/null)
ISP=$(cat /etc/xray/isp 2>/dev/null)
CITY=$(cat /etc/xray/city 2>/dev/null)

# Generate random username
Login="trial-$(tr -dc A-Z0-9 </dev/urandom | head -c 4)"
Pass="1"
iplim="1"

# Create user
useradd -e "$(date -d "1 day" +"%Y-%m-%d")" -s /bin/false -M "$Login" || {
    echo "ERROR: Failed to create user"
    exit 1
}

# Set password
echo -e "$Pass\n$Pass\n" | passwd "$Login" &> /dev/null
echo "### $Login $(date -d "1 day" +"%Y-%m-%d") $Pass" >> /etc/xray/ssh

# Schedule deletion
(crontab -l 2>/dev/null; echo "*/$TIMER_MINUTE * * * * userdel -r $Login && rm -f /etc/cron.d/trialssh${Login}") | crontab -
mv /var/spool/cron/crontabs/root /etc/cron.d/trialssh${Login}
chmod 600 /etc/cron.d/trialssh${Login}

# Generate output with Telegram-friendly formatting
cat <<EOF
===START_SSH_TRIAL===
⚡️ *TRIAL SSH ACCOUNT* ⚡️
━━━━━━━━━━━━━━━━━
🔹 *Username*: \`$Login\`
🔹 *Password*: \`$Pass\`
🔹 *Expired*: $TIMER_MINUTE Minutes
━━━━━━━━━━━━━━━━━
🌍 *Server Info*:
├─ 🏢 *ISP*: $ISP
└─ 🌆 *City*: $CITY
🔒 *Security*:
├─ 🔑 *IP Limit*: $iplim
└─ ⏳ *Auto-delete*: Yes
━━━━━━━━━━━━━━━━━
🔌 *Port Configuration*:
┌─ 🔹 *SSH*: 22
├─ 🔹 *Dropbear*: 109, 143
├─ 🔹 *WS*: 80, 8080
└─ 🔹 *SSL WS*: 443
━━━━━━━━━━━━━━━━━
📋 *Payload WS*:
\`\`\`
GET / HTTP/1.1[crlf]
Host: $domain[crlf]
Connection: Upgrade[crlf]
User-Agent: [ua][crlf]
Upgrade: websocket[crlf][crlf]
\`\`\`
━━━━━━━━━━━━━━━━━
⚠️ *Note*: Account will auto-delete after $TIMER_MINUTE minutes
===END_SSH_TRIAL===
EOF

exit 0
