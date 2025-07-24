#!/bin/bash
# ===============================================================
# Script: list_trojan_users.sh - Tampilan cantik daftar akun TROJAN
# ===============================================================

CONFIG_FILE="/etc/xray/config.json"
export LANG=en_US.UTF-8

if [ ! -f "$CONFIG_FILE" ]; then
    echo -e "🚫 *File konfigurasi tidak ditemukan:* \`$CONFIG_FILE\`"
    exit 1
fi

# Hitung jumlah akun TROJAN
NUMBER_OF_CLIENTS=$(grep -c -E "^#tr " "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo -e "🚫 *Tidak ada akun TROJAN yang aktif*"
else
    echo -e "🛡️ *D A F T A R  A K U N  T R O J A N*"
    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "〄  *USER*             *EXPIRED*"
    echo -e "―――――――――――――――――――――――――――――"

    # Ambil data user dari komentar #tr
    grep -E "^#tr " "$CONFIG_FILE" | nl -w1 -s ' ' | while read -r num line; do
        user=$(echo "$line" | awk '{print $2}')
        exp=$(echo "$line" | awk '{print $3}')
        printf "👤 %-15s ⏳ %s\n" "$user" "$exp"
    done

    echo -e "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "📊 *Total Akun*: *$NUMBER_OF_CLIENTS*"
fi

exit 0
