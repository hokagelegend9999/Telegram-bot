#!/bin/bash
# Script: list_vmess_users.sh
# Deskripsi: Mengambil daftar akun VMESS dari /etc/xray/config.json
#             Berdasarkan metode penyimpanan #vmg username expiry_date

CONFIG_FILE="/etc/xray/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: File konfigurasi XRay/V2Ray tidak ditemukan: $CONFIG_FILE" >&2
    exit 1
fi

# Hitung jumlah klien VMESS
NUMBER_OF_CLIENTS=$(grep -c -E "^#vmg " "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo "Belum ada akun VMESS yang terdaftar di sistem."
else
    echo "Daftar Akun VMESS:"
    echo "-------------------------------------"
    echo "No  User               Expired"
    echo "-------------------------------------"
    # Menggunakan grep, cut, dan nl seperti fungsi Anda
    grep -E "^#vmg " "$CONFIG_FILE" | cut -d ' ' -f 2-3 | nl -s '  ' | while read -r line; do
        # Menghapus kode warna ANSI jika ada (asumsi Anda memilikinya di config.json)
        # Jika tidak ada kode warna, baris ini tidak akan berpengaruh
        cleaned_line=$(echo "$line" | sed 's/\x1B\[[0-9;]*m//g')
        echo "$cleaned_line"
    done
    echo "-------------------------------------"
    echo "Total: ${NUMBER_OF_CLIENTS} akun."
fi

exit 0 # Pastikan script keluar dengan kode 0 untuk sukses
