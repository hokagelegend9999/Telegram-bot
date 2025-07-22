#!/bin/bash

# ==================================================================
#                       VMESS Account Deleter
#             (Adapted from user's del-vmess function)
# ==================================================================

# Error handling: Pastikan hanya 1 argumen yang diberikan (username)
if [ "$#" -ne 1 ]; then
    echo "⚠️ Error: Butuh 1 argumen: <username>"
    echo "Usage: $0 <username>"
    exit 1
fi

user="$1"
CONFIG_FILE="/etc/xray/config.json"
LOG_DIR="/etc/vmess/akun" # Direktori tempat file log akun disimpan
HOME_VPS_DIR="/home/vps/public_html" # Direktori untuk file .txt yang mungkin dibuat

echo "⏳ Memulai penghapusan akun VMESS untuk username: $user"

# --- Langkah 1: Memeriksa apakah username ada di konfigurasi dan mendapatkan exp date ---
# Penting: Kita butuh tanggal kadaluarsa (exp) untuk sed agar cocok dengan pola #vm user exp
# Jika user sudah expired, grep mungkin tidak menemukan entri.
# Oleh karena itu, kita akan mencari username saja atau mengambil semua baris #vm/#vmg.

# Cari baris yang mengandung username (dari #vmg atau #vm)
VMG_ENTRY=$(grep -E "^#vmg $user " "$CONFIG_FILE")
VM_ENTRY=$(grep -E "^#vm $user " "$CONFIG_FILE")

# Jika tidak ditemukan entri sama sekali
if [ -z "$VMG_ENTRY" ] && [ -z "$VM_ENTRY" ]; then
    echo "❌ Error: Username '$user' tidak ditemukan dalam konfigurasi Xray."
    exit 1
fi

# Dapatkan tanggal kadaluarsa dari salah satu entri yang ditemukan
# Ambil yang pertama ditemukan (misalnya dari VMG_ENTRY)
if [ ! -z "$VMG_ENTRY" ]; then
    exp=$(echo "$VMG_ENTRY" | awk '{print $3}' | head -n 1)
elif [ ! -z "$VM_ENTRY" ]; then
    exp=$(echo "$VM_ENTRY" | awk '{print $3}' | head -n 1)
else
    # Fallback jika somehow username ditemukan tapi pola exp tidak cocok
    echo "⚠️ Peringatan: Tidak dapat mengambil tanggal kadaluarsa untuk '$user'. Melanjutkan dengan penghapusan berdasarkan username saja (mungkin kurang presisi)."
    exp="" # Kosongkan exp agar sed mencari hanya username
fi

echo "⏳ Menghapus entri akun dari $CONFIG_FILE..."

# --- Langkah 2: Menghapus entri pengguna dari config.json berdasarkan pola yang benar ---
# Menggunakan pola yang ada di script del-vmess Anda: "/^#vmg $user $exp/,/^},{/d"
# Penting: Jika $exp kosong, sed akan mencari pola tanpa tanggal kadaluarsa yang spesifik.

# Hapus entri dari inbound VMESS (gRPC)
if [ -z "$exp" ]; then
    # Jika exp tidak diketahui, hapus berdasarkan username saja (kurang presisi tapi aman)
    sed -i "/^#vmg $user /,/^},{/d" "$CONFIG_FILE"
else
    sed -i "/^#vmg $user $exp/,/^},{/d" "$CONFIG_FILE"
fi

# Hapus entri dari inbound VMESS (WebSocket)
if [ -z "$exp" ]; then
    sed -i "/^#vm $user /,/^},{/d" "$CONFIG_FILE"
else
    sed -i "/^#vm $user $exp/,/^},{/d" "$CONFIG_FILE"
fi

# --- Verifikasi penghapusan (opsional, untuk debugging) ---
if grep -q "$user" "$CONFIG_FILE"; then
    echo "⚠️ Peringatan: Entri untuk username '$user' mungkin tidak sepenuhnya terhapus dari konfigurasi. Perlu pemeriksaan manual."
else
    echo "✅ Entri akun '$user' berhasil dihapus dari $CONFIG_FILE."
fi

# --- Langkah 3: Menghapus file log dan file terkait lainnya ---
echo "⏳ Menghapus file log dan file terkait..."

# Hapus file log akun utama
LOG_FILE="${LOG_DIR}/vmess-${user}.log"
if [ -f "$LOG_FILE" ]; then
    rm "$LOG_FILE"
    echo "✅ File log akun '$LOG_FILE' dihapus."
else
    echo "⚠️ Peringatan: File log akun '$LOG_FILE' tidak ditemukan."
fi

# Hapus file IP limit (dari script del-vmess Anda)
IP_LIMIT_FILE="/etc/vmess/${user}IP"
if [ -f "$IP_LIMIT_FILE" ]; then
    rm "$IP_LIMIT_FILE"
    echo "✅ File IP limit '$IP_LIMIT_FILE' dihapus."
else
    echo "⚠️ Peringatan: File IP limit '$IP_LIMIT_FILE' tidak ditemukan."
fi

# Hapus file login (dari script del-vmess Anda)
LOGIN_FILE="/etc/vmess/${user}login"
if [ -f "$LOGIN_FILE" ]; then
    rm "$LOGIN_FILE"
    echo "✅ File login '$LOGIN_FILE' dihapus."
else
    echo "⚠️ Peringatan: File login '$LOGIN_FILE' tidak ditemukan."
fi

# Hapus file .txt di public_html (dari script del-vmess Anda)
PUBLIC_HTML_FILE="${HOME_VPS_DIR}/vmess-${user}.txt"
if [ -f "$PUBLIC_HTML_FILE" ]; then
    rm "$PUBLIC_HTML_FILE"
    echo "✅ File public_html '$PUBLIC_HTML_FILE' dihapus."
else
    echo "⚠️ Peringatan: File public_html '$PUBLIC_HTML_FILE' tidak ditemukan."
fi


# --- Langkah 4: Merestart layanan Xray ---
echo "⏳ Merestart layanan Xray untuk menerapkan perubahan..."
systemctl restart xray # Menghapus > /dev/null 2>&1 sementara untuk melihat output jika ada error.
# Jika Anda yakin tidak ingin melihat output ini, tambahkan lagi: > /dev/null 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Layanan Xray berhasil direstart."
    echo ""
    echo "================================================="
    echo "🎉 Akun VMESS '$user' berhasil dihapus!"
    echo "================================================="
else
    echo "❌ Error: Gagal merestart layanan Xray."
    echo "Harap periksa status Xray secara manual dan restart jika perlu:"
    echo "  sudo systemctl status xray"
    echo "  sudo systemctl restart xray"
    exit 1 # Keluar dengan status error jika Xray gagal direstart
fi

exit 0 # Keluar dengan status sukses
