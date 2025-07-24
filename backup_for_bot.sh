#!/bin/bash
# ==================================================================
#       SKRIP BACKUP v2.0 - Telegram Bot Friendly
# ==================================================================
# Deskripsi: Membuat backup, menyertakan data akun, dan
#            menyediakan path lokal untuk dikirim via bot.

# --- Konfigurasi ---
IP=$(curl -sS ipv4.icanhazip.com)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="/root/backup_${TIMESTAMP}"
BACKUP_FILE="/root/backup_${IP}_${TIMESTAMP}.zip"
BACKUP_FILE_NAME="backup_${IP}_${TIMESTAMP}.zip"

# --- Proses Utama ---

# 1. Membuat direktori backup
echo "📁 Langkah 1: Membuat direktori backup..."
mkdir -p "$BACKUP_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Gagal membuat direktori backup."
    exit 1
fi

# 2. Menyalin file dan direktori penting
echo "⚙️  Langkah 2: Menyalin file sistem dan data akun..."
# File sistem dasar
cp -r /etc/passwd /etc/group /etc/shadow /etc/gshadow /etc/crontab "$BACKUP_DIR/" &>/dev/null
# File konfigurasi utama
cp -r /var/lib/kyt/ /etc/xray /var/www/html/ "$BACKUP_DIR/" &>/dev/null

# Menyalin folder data akun jika ada
[ -d "/etc/vmess" ] && cp -r /etc/vmess "$BACKUP_DIR/" &>/dev/null
[ -d "/etc/vless" ] && cp -r /etc/vless "$BACKUP_DIR/" &>/dev/null
[ -d "/etc/trojan" ] && cp -r /etc/trojan "$BACKUP_DIR/" &>/dev/null
echo "File berhasil disalin."

# 3. Membuat arsip ZIP
echo "🗜️  Langkah 3: Membuat arsip ZIP..."
cd "$BACKUP_DIR"
zip -r "$BACKUP_FILE" . &>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Gagal membuat arsip ZIP."
    rm -rf "$BACKUP_DIR"
    exit 1
fi
echo "Arsip ZIP dibuat: ${BACKUP_FILE_NAME}"

# 4. Upload ke Rclone (Opsional)
LINK="Tidak tersedia (rclone belum dikonfigurasi)"
if command -v rclone &> /dev/null; then
    echo "☁️  Langkah 4: Mengupload ke Google Drive..."
    rclone copy "$BACKUP_FILE" dr:backup/ &>/dev/null
    if [ $? -eq 0 ]; then
        echo "Upload berhasil. Mendapatkan link..."
        LINK=$(timeout 30 rclone link dr:backup/"$BACKUP_FILE_NAME")
        if [ -z "$LINK" ]; then
            LINK="Gagal mendapatkan link."
        fi
    else
        echo "Upload gagal. Periksa konfigurasi rclone."
    fi
else
    echo "Langkah 4: Dilewati. rclone tidak terinstal."
fi

# 5. Membersihkan direktori kerja (BUKAN FILE ZIP)
echo "🧹 Langkah 5: Membersihkan direktori kerja..."
rm -rf "$BACKUP_DIR" # Hanya hapus folder sumber, sisakan file .zip
echo "Pembersihan selesai."

# 6. Menghasilkan output akhir untuk bot
echo ""
echo "📊 --- Ringkasan Backup ---"
echo "FileName: ${BACKUP_FILE_NAME}"
echo "Status: Berhasil ✅"
echo "Link: ${LINK}"
echo "LocalPath: ${BACKUP_FILE}" # Memberikan path file untuk dikirim bot

exit 0
