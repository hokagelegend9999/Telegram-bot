#!/bin/bash

# Skrip backup dengan output yang lebih menarik untuk bot Telegram

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
echo "⚙️  Langkah 2: Menyalin file sistem..."
cp -r /etc/passwd /etc/group /etc/shadow /etc/gshadow /etc/crontab "$BACKUP_DIR/" &>/dev/null
cp -r /var/lib/kyt/ /etc/xray /var/www/html/ "$BACKUP_DIR/" &>/dev/null
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

# 4. Upload ke Rclone (Google Drive)
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

# 5. Membersihkan file lokal
echo "🧹 Langkah 5: Membersihkan file sementara..."
rm -f "$BACKUP_FILE"
rm -rf "$BACKUP_DIR"
echo "Pembersihan selesai."

# 6. Menghasilkan output akhir untuk bot
echo ""
echo "📊 --- Ringkasan Backup ---"
echo "File Name : ${BACKUP_FILE_NAME}"
echo "Status    : Berhasil ✅"
echo "Link      : ${LINK}"
