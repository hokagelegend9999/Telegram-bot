#!/bin/bash

# Script ini akan mengambil daftar pengguna SSH yang valid dari sistem
# dan mencoba menampilkan tanggal kadaluwarsa jika Anda menyimpannya.

# Metode 1: Mencantumkan pengguna sistem yang memiliki home directory
# Ini biasanya digunakan untuk akun SSH yang dibuat secara manual.
# Output: username
# Contoh: root, user1, user2
# cat /etc/passwd | grep -E '/home/|/usr/sbin/nologin|/bin/false' | grep -v 'root' | cut -d: -f1

# Metode 2: Mengambil informasi dari file log atau database kustom Anda
# Jika Anda menggunakan panel seperti X-UI atau script kustom yang menyimpan data user/expired date,
# Anda perlu menyesuaikan ini untuk membaca dari lokasi data panel/script Anda.
# Contoh: Asumsi Anda punya file /etc/ssh/expired_users.txt formatnya: username expired_date
# while read user exp_date; do
#   echo "$user $exp_date"
# done < /etc/ssh/expired_users.txt

# --- Contoh yang lebih realistis jika Anda menyimpan data di database SQLite lokal ---
# Asumsi: Anda punya database.db dan tabel accounts dengan kolom username, expiration_date, type
# Jika database.py Anda menggunakan SQLite, Anda perlu menginstal sqlite3 di server:
# sudo apt update && sudo apt install -y sqlite3

# Contoh panggil Python untuk ambil dari DB (membutuhkan Python script terpisah atau modifikasi database.py)
# Jika Anda menyimpan di database.py dan sudah terhubung ke DB nyata,
# maka tidak perlu script shell ini, langsung saja pakai logika database.py.

# Untuk demo ini, mari kita asumsikan output sederhana dari pengguna sistem
# dan Anda akan menyesuaikan untuk expired date.

# Jika pengguna dibuat dengan 'useradd -s /bin/false' atau nologin, mereka tetap bisa jadi akun SSH.
# Kita akan mencari user dengan UID > 999 (bukan user sistem) DAN memiliki home directory
# atau shell yang dibatasi (nologin, false, sbin/sh).
# Ini hanya contoh dasar, sesuaikan dengan cara Anda membuat user SSH.

# Versi dasar: Ambil semua user selain root dan nodya
# Anda mungkin perlu menyesuaikan filter 'grep -v' jika ada user lain yang bukan SSH
users=$(grep -E ':/home/|:/usr/sbin/nologin|:/bin/false' /etc/passwd | awk -F: '$3 >= 1000 && $1 != "nobody" {print $1}')

if [ -z "$users" ]; then
    echo "Belum ada akun SSH yang ditemukan di sistem."
else
    echo "Username             Status             Kadaluwarsa"
    echo "---------------------------------------------------"
    while IFS= read -r user; do
        # Anda harus mengimplementasikan logika untuk mendapatkan tanggal kadaluwarsa di sini
        # Ini adalah bagian yang paling sulit karena tergantung bagaimana Anda menyimpannya.
        # Jika Anda menggunakan script 'create_ssh.sh' untuk membuat user,
        # mungkin ada file di /etc/passwd_expired/username yang berisi tanggal expired.
        
        # Contoh dummy status/expired (Anda harus menggantinya dengan logika nyata)
        status="Aktif"
        expired_date="N/A" # <-- Implementasikan cara mengambil tanggal expired nyata!
        
        # Contoh mencari expired date di file kustom
        # if [ -f "/etc/expired_users/$user" ]; then
        #     expired_date=$(cat "/etc/expired_users/$user")
        # fi

        # Jika Anda menyimpan data di database, Anda perlu script Python kecil terpisah
        # yang terhubung ke database dan mencari tanggal expired user ini.
        
        printf "%-20s %-18s %-s\n" "$user" "$status" "$expired_date"
    done <<< "$users"
fi
