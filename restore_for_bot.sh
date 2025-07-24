#!/bin/bash
# ==================================================================
#       SKRIP RESTORE v1.0 - From Telegram Backup
# ==================================================================

# Validasi argumen
if [ "$#" -ne 1 ]; then
    echo "❌ Error: Butuh 1 argumen: path_ke_file_backup.zip"
    exit 1
fi

BACKUP_FILE="$1"
RESTORE_DIR="/root/restore_temp_$(date +%s)"

# --- Proses Utama ---

# 1. Cek apakah file backup ada
echo "🔎 Langkah 1: Memeriksa file backup..."
if [ ! -f "$BACKUP_FILE" ]; then
    echo "Error: File backup tidak ditemukan di '$BACKUP_FILE'."
    exit 1
fi
echo "File ditemukan."

# 2. Membuat direktori restore sementara
echo "📁 Langkah 2: Membuat direktori sementara..."
mkdir -p "$RESTORE_DIR"
if [ $? -ne 0 ]; then
    echo "Error: Gagal membuat direktori sementara."
    exit 1
fi

# 3. Ekstrak file backup
echo "🗜️  Langkah 3: Mengekstrak arsip..."
# Opsi -o untuk menimpa file tanpa bertanya
unzip -o "$BACKUP_FILE" -d "$RESTORE_DIR/" &>/dev/null
if [ $? -ne 0 ]; then
    echo "Error: Gagal mengekstrak file ZIP. File mungkin rusak."
    rm -rf "$RESTORE_DIR"
    exit 1
fi
echo "Ekstrak berhasil."

# 4. Menyalin file ke lokasi asli (OVERWRITE)
# Menggunakan rsync -a untuk menjaga perizinan dan menyalin secara rekursif
echo "⚙️  Langkah 4: Menyalin file ke sistem..."
if [ -d "$RESTORE_DIR/etc" ]; then
    rsync -a "$RESTORE_DIR/etc/" /etc/
fi
if [ -d "$RESTORE_DIR/var/lib/kyt" ]; then
    rsync -a "$RESTORE_DIR/var/lib/kyt/" /var/lib/kyt/
fi
if [ -d "$RESTORE_DIR/var/www/html" ]; then
    rsync -a "$RESTORE_DIR/var/www/html/" /var/www/html/
fi
echo "File sistem berhasil dipulihkan."

# 5. Restart layanan
echo "🔄 Langkah 5: Merestart layanan..."
systemctl restart xray > /dev/null 2>&1
echo "Layanan Xray berhasil direstart."

# 6. Membersihkan
echo "🧹 Langkah 6: Membersihkan file sementara..."
rm -f "$BACKUP_FILE" # Hapus file zip yang diupload
rm -rf "$RESTORE_DIR" # Hapus folder ekstrak
echo "Pembersihan selesai."

# 7. Output akhir
echo ""
echo "✅ --- Restore Selesai ---"
echo "Status: Berhasil"
echo "Semua data dari file backup telah dipulihkan."

exit 0
