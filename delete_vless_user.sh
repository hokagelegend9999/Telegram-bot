#!/bin/bash
# ===============================================================
# Script: delete_vless_user.sh
# Menghapus akun VLESS berdasarkan username.
# ===============================================================

# --- Validasi Input ---
if [ "$#" -ne 1 ]; then
    echo "❌ Error: Skrip ini membutuhkan satu argumen: <username>"
    echo "Penggunaan: $0 nama_pengguna"
    exit 1
fi

user="$1"
CONFIG_FILE="/etc/xray/config.json"
MARKER="#vl "

# --- Langkah 1: Cek apakah user ada berdasarkan penanda komentar ---
# Menggunakan [[:space:]] agar lebih fleksibel terhadap spasi atau tab
if ! grep -q -E "^${MARKER}${user}[[:space:]]" "$CONFIG_FILE"; then
    echo "❌ Error: Username '$user' tidak ditemukan."
    echo "   Akun mungkin sudah dihapus atau tidak pernah ada."
    exit 1
fi

echo "✅ Username '$user' ditemukan. Memulai proses penghapusan..."

# --- Langkah 2: Dapatkan UUID unik milik user dari baris komentar ---
# Diasumsikan formatnya: #vl user exp uuid
uuid=$(grep -E "^${MARKER}${user}[[:space:]]" "$CONFIG_FILE" | awk '{print $4}')

if [ -z "$uuid" ]; then
    echo "❌ Error: Gagal menemukan UUID untuk user '$user'. Proses dibatalkan."
    exit 1
fi

echo "⏳ UUID ditemukan: $uuid"

# --- Langkah 3: Hapus baris dari config.json ---
# 1. Hapus baris object JSON yang berisi UUID tersebut. Ini cara paling aman.
sed -i '/"id": "'"$uuid"'"/d' "$CONFIG_FILE"
echo "✅ Baris data JSON untuk '$user' telah dihapus."

# 2. Hapus baris komentar penanda #vl.
sed -i "/^${MARKER}${user}[[:space:]]/d" "$CONFIG_FILE"
echo "✅ Baris komentar untuk '$user' telah dihapus."

# --- Langkah 4: Hapus file-file terkait (jika ada) ---
# Disesuaikan dari contoh skrip Anda sebelumnya
echo "⏳ Menghapus file-file sisa..."
rm -f "/etc/vless/akun/log-create-${user}.log"
echo "✅ File sisa telah dibersihkan."

# --- Langkah 5: Restart layanan Xray ---
echo "⏳ Merestart layanan Xray..."
if systemctl restart xray; then
    echo "🎉 Berhasil! Akun VLESS '$user' telah dihapus sepenuhnya."
else
    echo "❌ Peringatan: Gagal merestart layanan Xray. Coba restart manual."
    echo "   sudo systemctl restart xray"
    exit 1
fi

exit 0
