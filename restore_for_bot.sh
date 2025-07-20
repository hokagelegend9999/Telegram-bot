#!/bin/bash

# Skrip untuk merestore backup terbaru dari rclone (Google Drive)

# --- Variabel ---
RCLONE_REMOTE="dr:backup/" # Sesuaikan jika nama remote rclone Anda berbeda
RESTORE_DIR="/root/restore_temp"

# --- Proses Utama ---
echo "⚙️  Memulai proses restore..."

# 1. Cari file backup terbaru di rclone
echo "1. Mencari backup terbaru di Google Drive..."
LATEST_BACKUP=$(rclone lsf "$RCLONE_REMOTE" --files-only | sort -r | head -n 1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ Gagal: Tidak ada file backup yang ditemukan di ${RCLONE_REMOTE}."
    exit 1
fi
echo "Backup terbaru ditemukan: ${LATEST_BACKUP}"

# 2. Buat direktori sementara dan unduh backup
echo "2. Mengunduh file backup..."
mkdir -p "$RESTORE_DIR"
rclone copy "${RCLONE_REMOTE}${LATEST_BACKUP}" "$RESTORE_DIR"
if [ $? -ne 0 ]; then
    echo "❌ Gagal: Tidak dapat mengunduh file dari rclone."
    rm -rf "$RESTORE_DIR"
    exit 1
fi

# 3. Ekstrak file backup
echo "3. Mengekstrak file .zip..."
BACKUP_FILE_PATH="$RESTORE_DIR/$LATEST_BACKUP"
unzip -o "$BACKUP_FILE_PATH" -d "$RESTORE_DIR/extracted" &>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Gagal: Tidak dapat mengekstrak file backup."
    rm -rf "$RESTORE_DIR"
    exit 1
fi

# 4. Timpa file sistem (Langkah Paling Kritis!)
echo "4. Menyalin file ke sistem (overwrite)..."
cp -rf "$RESTORE_DIR/extracted/etc/" /
cp -rf "$RESTORE_DIR/extracted/var/" /
cp -rf "$RESTORE_DIR/extracted/root/" /
echo "File sistem berhasil ditimpa."

# 5. Restart semua layanan terkait
echo "5. Merestart semua layanan..."
systemctl restart nginx xray cron ssh dropbear openvpn ws-stunnel &>/dev/null

# 6. Membersihkan file sementara
echo "6. Membersihkan direktori sementara..."
rm -rf "$RESTORE_DIR"

echo ""
echo "✅ Restore Selesai! Semua konfigurasi dari backup '${LATEST_BACKUP}' telah diterapkan."
