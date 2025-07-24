#!/bin/bash
# Menampilkan daftar akun SSH aktif dengan format elegan untuk Telegram

CONFIG_FILE="/etc/xray/ssh"
export LANG=en_US.UTF-8

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "🚫 *File konfigurasi tidak ditemukan!*"
    exit 1
fi

NUMBER_OF_CLIENTS=$(grep -c -E "^### " "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo -e "🚫 *Tidak ada akun SSH yang aktif*"
else
    echo -e "✨ *D A F T A R  A K U N  S S H* ✨"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "〄  *USER*             *EXPIRED*"
    echo -e "―――――――――――――――――――――――――――――"

    # Loop daftar user dari file config
    grep -E "^### " "$CONFIG_FILE" | while read -r line; do
        user=$(echo "$line" | awk '{print $2}')
        exp=$(echo "$line" | awk '{print $3}')
        printf "👤 %-15s ⏳ %s\n" "$user" "$exp"
    done

    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "📊 *Total Akun*: *$NUMBER_OF_CLIENTS*"
fi
