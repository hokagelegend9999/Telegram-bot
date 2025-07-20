#!/bin/bash

# Skrip untuk memeriksa status layanan, dirancang untuk output bot Telegram

# Fungsi untuk memeriksa status layanan dan memberikan output sederhana
check_service() {
    if systemctl is-active --quiet "$1"; then
        echo "ONLINE ✅"
    else
        echo "OFFLINE ❌"
    fi
}

# --- Informasi Sistem ---
CPU_INFO=$(lscpu | grep 'Model name' | awk -F: '{print $2}' | sed 's/^[ \t]*//')
CPU_CORES=$(lscpu | grep 'CPU(s):' | head -n 1 | awk '{print $2}')
UPTIME=$(uptime -p | sed 's/up //')

echo "--- System Information ---"
echo "CPU       : ${CPU_INFO}"
echo "Cores     : ${CPU_CORES} Core"
echo "Uptime    : ${UPTIME}"
echo ""
echo "--- Service Status ---"

# --- Daftar Layanan ---
# Tambahkan atau hapus nama service di daftar ini jika perlu
services_to_check=(
    "nginx"
    "xray"
    "ssh"
    "dropbear"
    "openvpn"
    "cron"
    "fail2ban"
    "ws-stunnel"
    "udp-custom"
)

# Loop dan cetak status setiap layanan
for service in "${services_to_check[@]}"; do
    # Format nama agar rapi
    printf "%-12s: %s\n" "$(echo "$service" | tr 'a-z' 'A-Z')" "$(check_service "$service")"
done
