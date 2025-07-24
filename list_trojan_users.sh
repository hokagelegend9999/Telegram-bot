#!/bin/bash
# ==================================================================
#       SKRIP v2.0 - LIST TROJAN USERS (BEAUTIFIED)
# ==================================================================
# Deskripsi: Menampilkan daftar akun TROJAN dengan format yang indah.

CONFIG_FILE="/etc/xray/config.json"

# Fungsi untuk menghapus kode warna ANSI (jaga-jaga)
strip_ansi_colors() {
    sed 's/\x1B\[[0-9;]*m//g'
}

if [ ! -f "$CONFIG_FILE" ]; then
    echo "ERROR: File konfigurasi XRay tidak ditemukan: $CONFIG_FILE" >&2
    exit 1
fi

# Mengambil data user dari komentar #tr
# Format output: "1 user1 2025-12-31"
TROJAN_USERS=$(grep -E "^#tr " "$CONFIG_FILE" | awk '{print $2, $3}' | nl -w1 -s ' ' | while read -r num user exp_date; do
    user_clean=$(echo "$user" | strip_ansi_colors)
    exp_date_clean=$(echo "$exp_date" | strip_ansi_colors)
    echo "$num $user_clean $exp_date_clean"
done)

# --- Mulai Membuat Tampilan ---

# Header Utama
echo "═══════[ DAFTAR AKUN TROJAN ]═══════"

if [ -z "$TROJAN_USERS" ]; then
    echo "      Belum ada akun TROJAN"
    echo "      yang terdaftar di sistem."
else
    # Menghitung total akun
    TOTAL_AKUN=$(echo "$TROJAN_USERS" | wc -l)
    echo " Total Akun: ${TOTAL_AKUN}"
    echo "───────────────────────────────────────"
    # Header Tabel
    printf " No. | Username             | Expired\n"
    echo "───────────────────────────────────────"

    # Body Tabel (Loop melalui data user)
    echo "$TROJAN_USERS" | while read -r num user exp; do
        printf " %-3s | %-20s | %s\n" "$num" "$user" "$exp"
    done

    echo "───────────────────────────────────────"
    # Footer/Instruksi
    echo "💡 Tip: Ketik nomor akun untuk"
    echo "   melihat detail konfigurasi."
    echo ""
    echo "   Ketik 0 untuk kembali."
fi

# Footer Utama
echo "═══════════════════════════════════"

exit 0
