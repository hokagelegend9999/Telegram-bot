#!/bin/bash

# Skrip restart layanan untuk dipanggil oleh bot Telegram

# Daftar layanan yang akan di-restart
services=(
    "nginx"
    "xray"
    "rc-local"
    "ws-dropbear"
    "openvpn"
    "cron"
    "haproxy"
    "netfilter-persistent"
    "squid"
    "udp-custom"
    "ws-stunnel"
    "badvpn1"
    "badvpn2"
    "badvpn3"
)

# Header output
echo "--- Proses Restart Layanan Dimulai ---"
echo ""

# Reload daemon
echo "Reloading systemd daemon..."
systemctl daemon-reload
echo "Status: OK"
echo "---------------------------------"

# Loop untuk me-restart setiap layanan
for service in "${services[@]}"; do
    # Cek apakah layanan ada sebelum mencoba me-restart
    if systemctl list-units --type=service --all | grep -q "${service}.service"; then
        echo "Restarting ${service}..."
        systemctl restart "${service}"
        if [ $? -eq 0 ]; then
            echo "Status: OK"
        else
            echo "Status: FAILED"
        fi
        echo "---------------------------------"
    fi
done

echo "✅ Semua layanan yang relevan telah di-restart."
