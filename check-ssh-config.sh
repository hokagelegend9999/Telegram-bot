#!/bin/bash

# =================================================================
#        Skrip Cek Konfigurasi User SSH untuk Hokage-BOT (Lebih Pintar)
# =================================================================
# Deskripsi: Skrip ini bisa menangani dua jenis akun dengan mencari
#            log detail terlebih dahulu, lalu file .txt sebagai alternatif.
# =================================================================

# Validasi input
if [ "$#" -ne 1 ]; then
    echo "<b>Error:</b> Nama pengguna tidak diberikan."
    exit 1
fi

USERNAME=$1

# Definisikan lokasi kedua jenis file konfigurasi
DETAILED_LOG="/etc/xray/sshx/akun/log-create-${USERNAME}.log"
SIMPLE_CONFIG="/home/vps/public_html/ssh-${USERNAME}.txt"

# --- Logika Pengecekan Cerdas ---

# Prioritas 1: Cek apakah ada log detail (dibuat oleh panel/skrip advance)
if [ -f "$DETAILED_LOG" ]; then
    # Jika ada, tampilkan isinya setelah dibersihkan dari kode warna
    echo "✅ <b>Konfigurasi Lengkap (dari Log Detail)</b>"
    echo
    cat "$DETAILED_LOG" | sed -r "s/\x1B\[[0-9;]*[mK]//g"
    exit 0
fi

# Prioritas 2: Jika log detail tidak ada, cek file .txt sederhana (dibuat oleh bot)
if [ -f "$SIMPLE_CONFIG" ]; then
    # Jika ada, tampilkan isinya
    echo "✅ <b>Konfigurasi Dasar (dari File .txt)</b>"
    echo
    echo "<pre>"
    cat "$SIMPLE_CONFIG"
    echo "</pre>"
    exit 0
fi

# Jika keduanya tidak ada, barulah tampilkan error
echo "❌ <b>Konfigurasi Tidak Ditemukan</b>"
echo "Tidak dapat menemukan file log detail ataupun file info .txt untuk user <code>$USERNAME</code>."
# Lakukan pengecekan terakhir untuk memastikan user benar-benar ada di sistem
if id "$USERNAME" &>/dev/null; then
    echo "User <code>$USERNAME</code> terdaftar di sistem, namun file konfigurasinya tidak ditemukan."
else
    echo "User <code>$USERNAME</code> juga tidak terdaftar sebagai pengguna di sistem Linux."
fi

exit 1
