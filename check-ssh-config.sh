#!/bin/bash

# =================================================================
#        Skrip Cek Konfigurasi User SSH untuk Hokage-BOT (Perbaikan)
# =================================================================
# Deskripsi: Skrip ini mengambil detail konfigurasi dari file .txt
#            yang dibuat saat user SSH dibuat.
# =================================================================

# Validasi input
if [ "$#" -ne 1 ]; then
    echo "<b>Error:</b> Nama pengguna tidak diberikan."
    exit 1
fi

USERNAME=$1
CONFIG_FILE="/home/vps/public_html/ssh-${USERNAME}.txt"

# --- Validasi Baru ---
# 1. Cek apakah user ada di sistem Linux
if ! id "$USERNAME" &>/dev/null; then
    echo "❌ <b>User Tidak Ditemukan</b>"
    echo "Akun dengan username <code>$USERNAME</code> tidak ada di server ini."
    exit 1
fi

# 2. Cek apakah file konfigurasinya ada
if [ ! -f "$CONFIG_FILE" ]; then
    echo "❌ <b>File Konfigurasi Tidak Ditemukan</b>"
    echo "Tidak dapat menemukan file info untuk user <code>$USERNAME</code>."
    echo "Lokasi yang dicari: $CONFIG_FILE"
    exit 1
fi

# --- Aksi Utama ---
# Tampilkan isi dari file konfigurasi tersebut.
# Kita bungkus dengan <pre> agar formatnya rapi di Telegram.

echo "✅ <b>Konfigurasi untuk user <code>$USERNAME</code></b>"
echo
# Menggunakan <pre> untuk menjaga spasi dan format asli dari file .txt
echo "<pre>"
cat "$CONFIG_FILE"
echo "</pre>"

exit 0
