#!/bin/bash
# Script: list_ssh_users.sh
# Deskripsi: Mengambil daftar akun SSH dari /etc/xray/ssh
#            Berdasarkan metode penyimpanan ### username expiry_date
# Output: Daftar akun dalam format yang mudah diparsing (No, User, Expired)

CONFIG_FILE="/etc/xray/ssh" # File yang mengandung daftar user dan expired date

# Fungsi untuk menghapus kode warna ANSI
strip_ansi_colors() {
    sed 's/\x1B\[[0-9;]*m//g'
}

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: File daftar SSH users tidak ditemukan: $CONFIG_FILE" >&2
    exit 1
fi

# Hitung jumlah klien SSH
# Menggunakan pola yang Anda tunjukkan: "^### "
NUMBER_OF_CLIENTS=$(grep -c -E "^### " "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo "NO_CLIENTS" # Tanda khusus jika tidak ada klien
else
    # Ambil baris yang dimulai dengan ###, kemudian ekstrak kolom ke-2 (username)
    # dan kolom ke-3 (expired date) menggunakan awk.
    # Setelah itu, tambahkan nomor baris menggunakan nl.
    # Output: "1 user1 2025-12-31"
    grep -E "^### " "$CONFIG_FILE" | awk '{print $2, $3}' | nl -w1 -s ' ' | while read -r num user exp_date; do
        user_clean=$(echo "$user" | strip_ansi_colors)
        exp_date_clean=$(echo "$exp_date" | strip_ansi_colors)
        echo "$num $user_clean $exp_date_clean"
    done
fi

exit 0
