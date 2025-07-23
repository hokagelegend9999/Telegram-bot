#!/bin/bash
# Script: list_vmess_users.sh
# Deskripsi: Mengambil daftar akun VMESS dari /etc/xray/config.json
#            Berdasarkan metode penyimpanan #vmg username expiry_date
# Output: Daftar akun dalam format yang mudah diparsing (No, User, Expired)

CONFIG_FILE="/etc/xray/config.json"

# Fungsi untuk menghapus kode warna ANSI
strip_ansi_colors() {
    sed 's/\x1B\[[0-9;]*m//g'
}

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: File konfigurasi XRay/V2Ray tidak ditemukan: $CONFIG_FILE" >&2
    exit 1
fi

# Hitung jumlah klien VMESS
NUMBER_OF_CLIENTS=$(grep -c -E "^#vmg " "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo "NO_CLIENTS" # Tanda khusus jika tidak ada klien
else
    # Menggunakan awk untuk mengekstrak username dan expired date,
    # lalu nl untuk menambahkan nomor baris.
    # Output: "1 user1 2025-12-31"
    grep -E "^#vmg " "$CONFIG_FILE" | awk '{print $2, $3}' | nl -w1 -s ' ' | while read -r num user exp_date; do
        user_clean=$(echo "$user" | strip_ansi_colors)
        exp_date_clean=$(echo "$exp_date" | strip_ansi_colors)
        echo "$num $user_clean $exp_date_clean"
    done
fi

exit 0
