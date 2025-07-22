#!/bin/bash

# =================================================================
#        Skrip Cek Konfigurasi User SSH untuk Hokage-BOT
# =================================================================
# Deskripsi: Skrip ini mengambil log pembuatan asli dari user
#            tertentu dan membersihkan kode warna untuk output bot.
# =================================================================

# Validasi input
if [ "$#" -ne 1 ]; then
    echo "<b>Error:</b> Nama pengguna tidak diberikan."
    exit 1
fi

USERNAME=$1
LOG_FILE="/etc/xray/sshx/akun/log-create-${USERNAME}.log"

# Validasi apakah user terdaftar di file utama
# -q (quiet) agar tidak ada output, hanya cek status exit
if ! grep -q -E "^### $USERNAME " "/etc/xray/ssh"; then
    echo "❌ <b>User Tidak Ditemukan</b>"
    echo "Akun dengan username <code>$USERNAME</code> tidak terdaftar di file /etc/xray/ssh."
    exit 1
fi

# Validasi apakah file log ada
if [ ! -f "$LOG_FILE" ]; then
    echo "❌ <b>Log Tidak Ditemukan</b>"
    echo "File log untuk user <code>$USERNAME</code> tidak ditemukan di: $LOG_FILE"
    exit 1
fi

# Ambil konten log dan bersihkan dari kode warna ANSI
# Regex ini akan menghapus semua escape sequence warna (cth: \x1B[1;37m)
CONFIG_DETAILS=$(cat "$LOG_FILE" | sed -r "s/\x1B\[[0-9;]*[mK]//g")

# Tampilkan output yang sudah bersih
echo -e "$CONFIG_DETAILS"

exit 0
