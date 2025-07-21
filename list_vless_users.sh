#!/bin/bash
# Script: list_vless_users.sh
# Deskripsi: Mengambil daftar akun VLESS langsung dari /etc/xray/config.json

# Pastikan 'jq' terinstal: sudo apt install -y jq

CONFIG_FILE="/etc/xray/config.json"

if [ ! -f "$CONFIG_FILE" ]; then
    echo "Error: File konfigurasi XRay/V2Ray tidak ditemukan: $CONFIG_FILE" >&2
    exit 1
fi

# Cek apakah file JSON valid sebelum diproses
if ! jq -e . "$CONFIG_FILE" > /dev/null; then
    echo "Error: File konfigurasi JSON tidak valid: $CONFIG_FILE" >&2
    exit 1
fi

echo "Username             UUID                               Kadaluwarsa"
echo "------------------------------------------------------------------"

# Ekstrak data VLESS dari config.json
# Kita mencari 'inbounds' dengan 'protocol == "vless"'
# Kemudian di dalamnya, kita ambil 'clients' dari 'settings'
# Untuk setiap klien, kita ambil 'email' (username) dan 'id' (UUID).
# expiryTime perlu dikonversi dari milidetik.
jq_query='
.inbounds[] |
select(.protocol == "vless") |
.settings.clients[] |
"\(.email // .id // "N/A_Username") \(.id // "N/A_UUID") \(if .expiryTime then (.expiryTime | tostring) else "0" end) \(if .totalUsed then (.totalUsed | tostring) else "0" end) \(if .limitIp then (.limitIp | tostring) else "0" end)"
'

VLESS_USERS_DATA=$(cat "$CONFIG_FILE" | jq -r "$jq_query")

if [ -z "$VLESS_USERS_DATA" ] || [ "$VLESS_USERS_DATA" == "null" ]; then
    echo "Belum ada akun VLESS yang ditemukan di $CONFIG_FILE."
else
    echo "$VLESS_USERS_DATA" | while read email_or_id uuid expiry_ms total_used limit_ip; do
        # Format tanggal kadaluwarsa
        if [ "$expiry_ms" != "0" ] && [ "$expiry_ms" != "null" ]; then
            # Konversi milidetik ke detik
            expiry_date=$(date -d "@$((expiry_ms / 1000))" +"%Y-%m-%d %H:%M")
        else
            expiry_date="Tidak Terbatas"
        fi
        
        printf "%-20s %-35s %-s\n" "$email_or_id" "$uuid" "$expiry_date"
        # Optional: printf "    Penggunaan: %s, Limit IP: %s\n" "$formatted_used" "$limit_ip"
    done
fi

exit 0 # Pastikan script keluar dengan kode 0 untuk sukses
