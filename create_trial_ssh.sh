#!/bin/bash

# =================================================================
#        Skrip Pembuatan Akun Trial SSH untuk Hokage-BOT
# =================================================================
# Dijalankan oleh bot untuk membuat akun trial dan mengirim
# detailnya kembali ke pengguna melalui bot.
# =================================================================

# --- Konfigurasi Awal ---
# Durasi trial dalam menit. Bot akan mengganti ini jika perlu.
TIMER_MINUTE="10" 

# --- Mengambil Informasi Sistem ---
# Mengambil variabel penting dari file konfigurasi di VPS
domain=$(cat /etc/xray/domain 2>/dev/null)
sldomain=$(cat /etc/xray/dns 2>/dev/null)
slkey=$(cat /etc/slowdns/server.pub 2>/dev/null)
ISP=$(cat /etc/xray/isp 2>/dev/null)
CITY=$(cat /etc/xray/city 2>/dev/null)

# --- Membuat Detail Akun ---
# Membuat username unik untuk akun trial
Login="Trial-$(tr -dc A-Z0-9 </dev/urandom | head -c 4)"
Pass="1" # Password default
iplim="1" # Batas IP default

# --- Membuat User di Sistem ---
# Menambahkan user baru dengan masa aktif 1 hari (akan dihapus oleh cron)
# Opsi -s /bin/false berarti user tidak bisa login ke shell interaktif
useradd -e "$(date -d "1 day" +"%Y-%m-%d")" -s /bin/false -M "$Login"
if [ $? -ne 0 ]; then
    echo "Error: Gagal membuat user baru."
    exit 1
fi

# Mengatur password untuk user baru
echo -e "$Pass\n$Pass\n" | passwd "$Login" &> /dev/null

# Menyimpan catatan user di file log
echo "### $Login $(date -d "1 day" +"%Y-%m-%d") $Pass" >> /etc/xray/ssh

# --- Membuat Jadwal Penghapusan Otomatis ---
# Membuat cron job untuk menghapus user setelah TIMER_MINUTE
# Ini akan membuat file di /etc/cron.d/
(crontab -l 2>/dev/null; echo "*/$TIMER_MINUTE * * * * userdel -r $Login && rm -f /etc/cron.d/trialssh${Login}") | crontab -
mv /var/spool/cron/crontabs/root /etc/cron.d/trialssh${Login}
chmod 600 /etc/cron.d/trialssh${Login}


# --- Menyiapkan Pesan Output untuk Bot ---
# Teks ini akan dicetak ke terminal dan ditangkap oleh bot Python
# untuk dikirim ke pengguna di Telegram.
cat << EOT
◇━━━━━━━━━━━━━━━━━◇
<b>Trial SSH Premium Account</b>
◇━━━━━━━━━━━━━━━━━◇
<b>Username</b>      : <code>$Login</code>
<b>Password</b>      : <code>$Pass</code>
<b>Expired On</b>      : $TIMER_MINUTE Minutes
◇━━━━━━━━━━━━━━━━━◇
<b>Host</b>            : <code>$domain</code>
<b>Host Slowdns</b>    : <code>$sldomain</code>
<b>ISP</b>             : $ISP
<b>City</b>            : $CITY
<b>Login Limit</b>     : ${iplim} IP
◇━━━━━━━━━━━━━━━━━◇
<b>Port OpenSSH</b>    : 22
<b>Port Dropbear</b>   : 109, 143
<b>Port SSH WS</b>     : 80, 8080
<b>Port SSH SSL WS</b> : 443
<b>Port SSL/TLS</b>    : 8443, 8880
<b>Port OVPN WS SSL</b>: 2086
<b>BadVPN UDP</b>      : 7100, 7200, 7300
◇━━━━━━━━━━━━━━━━━◇
<b>Payload WS</b>:
<code>GET / HTTP/1.1[crlf]Host: $domain[crlf]Connection: Upgrade[crlf]User-Agent: [ua][crlf]Upgrade: websocket[crlf][crlf]</code>
◇━━━━━━━━━━━━━━━━━◇
EOT

exit 0
