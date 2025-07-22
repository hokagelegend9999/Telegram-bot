#!/bin/bash

# =================================================================
#           Skrip Penghapusan Akun SSH untuk Hokage-BOT
# =================================================================
# Deskripsi: Skrip ini menghapus user SSH dari sistem dan
#            file info terkait.
# =================================================================

# --- Validasi Input ---
if [ "$#" -ne 1 ]; then
    echo "<b>Error:</b> Nama pengguna tidak diberikan."
    echo "Penggunaan: $0 <username>"
    exit 1
fi

USERNAME=$1
FILE_INFO="/home/vps/public_html/ssh-${USERNAME}.txt"

# --- Validasi User ---
# Periksa apakah user benar-benar ada sebelum mencoba menghapus
if ! id "$USERNAME" &>/dev/null; then
    echo "<b>Peringatan:</b> User <code>$USERNAME</code> tidak ditemukan di sistem."
    exit 1
fi

# --- Proses Penghapusan ---
# Hapus user dan direktori home-nya (-r flag)
userdel -r "$USERNAME" &>/dev/null

# Hapus file info di web server jika ada
if [ -f "$FILE_INFO" ]; then
    rm -f "$FILE_INFO"
fi

# --- Menampilkan Output Konfirmasi untuk Bot Telegram ---
cat << EOF
✅ <b>Berhasil Dihapus</b>

Akun SSH dengan detail berikut telah dihapus secara permanen dari server:

<b>Username:</b> <code>$USERNAME</code>

Semua data dan file terkait telah dibersihkan.
EOF

exit 0
