#!/bin/bash
# Script: list_trojan_users.sh
# Deskripsi: Mengambil daftar akun TROJAN dari /etc/xray/config.json
#            Berdasarkan metode penyimpanan #tr username expiry_date
# Output: Daftar akun dalam format yang mudah diparsing (No, User, Expired)

CONFIG_FILE="/etc/xray/config.json" # Lokasi akun Trojan Anda

# Fungsi untuk menghapus kode warna ANSI
strip_ansi_colors() {
    sed 's/\x1B\[[0-9;]*m//g'
}

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: File konfigurasi Trojan tidak ditemukan: $CONFIG_FILE" >&2
    exit 1
fi

# Hitung jumlah klien Trojan
USER_PATTERN="^#tr " # Pola yang Anda tunjukkan
NUMBER_OF_CLIENTS=$(grep -c -E "$USER_PATTERN" "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo "NO_CLIENTS" # Tanda khusus jika tidak ada klien
else
    # Ambil baris yang sesuai dengan pola, kemudian ekstrak kolom ke-2 (username)
    # dan kolom ke-3 (expired date) menggunakan awk.
    # Setelah itu, tambahkan nomor baris menggunakan nl.
    # Output: "1 user1 2025-12-31" (tanpa formatting tambahan atau newline eksplisit)
    grep -E "$USER_PATTERN" "$CONFIG_FILE" | awk '{print $2, $3}' | nl -w1 -s ' ' | while read -r num user exp_date; do
        user_clean=$(echo "$user" | strip_ansi_colors)
        exp_date_clean=$(echo "$exp_date" | strip_ansi_colors)
        echo "$num $user_clean $exp_date_clean" # Echo tanpa -e dan tanpa \n
    done
fi

exit 0
