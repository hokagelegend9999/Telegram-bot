#!/bin/bash
# ===============================================================
# Script: delete_trojan_user.sh
# Menghapus akun Trojan berdasarkan username.
# ===============================================================

# --- Validasi Input ---
if [ "$#" -ne 1 ]; then
    echo "❌ Error: Skrip ini membutuhkan satu argumen: <username>"
    echo "Penggunaan: $0 nama_pengguna"
    exit 1
fi

user="$1"
CONFIG_FILE="/etc/xray/config.json"

# --- Langkah 1: Cek apakah user ada berdasarkan penanda komentar ---
# Mencari penanda #tr atau #trg
if ! grep -q -E "^#tr[g]* ${user}[[:space:]]" "$CONFIG_FILE"; then
    echo "❌ Error: Username '$user' tidak ditemukan."
    echo "   Akun mungkin sudah dihapus atau tidak pernah ada."
    exit 1
fi

echo "✅ Username '$user' ditemukan. Memulai proses penghapusan..."

# --- Langkah 2: Dapatkan UUID (password) unik milik user ---
# UUID ada di baris #tr (Trojan WS)
uuid=$(grep -E "^#tr ${user}[[:space:]]" "$CONFIG_FILE" | awk '{print $4}')

if [ -z "$uuid" ]; then
    echo "❌ Error: Gagal menemukan UUID (password) untuk user '$user'. Proses dibatalkan."
    exit 1
fi

echo "⏳ UUID (Password) ditemukan: $uuid"

# --- Langkah 3: Hapus baris dari config.json ---
# 1. Hapus baris object JSON yang berisi password (UUID) tersebut.
sed -i '/"password": "'"$uuid"'"/d' "$CONFIG_FILE"
echo "✅ Baris data JSON untuk '$user' telah dihapus."

# 2. Hapus baris komentar penanda #tr dan #trg.
sed -i "/^#tr[g]* ${user}[[:space:]]/d" "$CONFIG_FILE"
echo "✅ Baris komentar untuk '$user' telah dihapus."

# --- Langkah 4: Hapus file log terkait ---
echo "⏳ Menghapus file-file sisa..."
rm -f "/etc/trojan/akun/log-create-${user}.log"
echo "✅ File sisa telah dibersihkan."

# --- Langkah 5: Restart layanan Xray ---
echo "⏳ Merestart layanan Xray..."
if systemctl restart xray; then
    echo "🎉 Berhasil! Akun Trojan '$user' telah dihapus sepenuhnya."
else
    echo "❌ Peringatan: Gagal merestart layanan Xray. Coba restart manual."
    echo "   sudo systemctl restart xray"
    exit 1
fi

exit 0
