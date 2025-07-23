#!/bin/bash
# Script: list_trojan_users.sh
# Deskripsi: Menampilkan daftar akun TROJAN dengan tampilan yang menarik
# Author: Your Name
# Version: 1.1

CONFIG_FILE="/etc/xray/config.json" # Lokasi akun Trojan Anda

# Fungsi untuk warna dan styling
bold=$(tput bold)
reset=$(tput sgr0)
red=$(tput setaf 1)
green=$(tput setaf 2)
yellow=$(tput setaf 3)
blue=$(tput setaf 4)
magenta=$(tput setaf 5)
cyan=$(tput setaf 6)

# Icon menggunakan emoji
icon_user="👤"
icon_key="🔑"
icon_calendar="📅"
icon_warning="⚠️"
icon_error="❌"
icon_success="✅"

# Fungsi untuk header
print_header() {
    clear
    echo "${bold}${cyan}"
    echo "┌────────────────────────────────────────────────────┐"
    echo "│           ${icon_key} ${magenta}TROJAN USER LIST ${cyan}${icon_key}           │"
    echo "└────────────────────────────────────────────────────┘"
    echo "${reset}"
}

# Fungsi untuk footer
print_footer() {
    echo "${bold}${cyan}"
    echo "┌────────────────────────────────────────────────────┐"
    echo "│  ${icon_warning} ${yellow}Total Users: ${bold}${blue}$NUMBER_OF_CLIENTS ${cyan}${icon_warning}                 │"
    echo "└────────────────────────────────────────────────────┘"
    echo "${reset}"
}

# Fungsi untuk menghapus kode warna ANSI
strip_ansi_colors() {
    sed 's/\x1B\[[0-9;]*m//g'
}

# Main program
print_header

if [ ! -f "$CONFIG_FILE" ]; then
    echo "${icon_error} ${red}ERROR: File konfigurasi Trojan tidak ditemukan!${reset}"
    echo "${yellow}Lokasi yang dicari: ${bold}$CONFIG_FILE${reset}"
    exit 1
fi

# Hitung jumlah klien Trojan
NUMBER_OF_CLIENTS=$(grep -c -E "^#tr " "$CONFIG_FILE")

if [[ ${NUMBER_OF_CLIENTS} == '0' ]]; then
    echo "${icon_warning} ${yellow}Tidak ada user Trojan yang ditemukan!${reset}"
else
    # Header tabel
    echo "${bold}${blue}┌─────┬──────────────────────┬──────────────────────┐${reset}"
    echo "${bold}${blue}│ ${green}No.  │ ${icon_user} ${cyan}Username          │ ${icon_calendar} ${cyan}Expired Date     ${blue}│${reset}"
    echo "${bold}${blue}├─────┼──────────────────────┼──────────────────────┤${reset}"

    # Ambil dan tampilkan data user
    grep -E "^#tr " "$CONFIG_FILE" | awk '{print $2, $3}' | nl -w1 -s ' ' | while read -r num user exp_date; do
        user_clean=$(echo "$user" | strip_ansi_colors)
        exp_date_clean=$(echo "$exp_date" | strip_ansi_colors)
        
        # Warna berdasarkan masa aktif (contoh sederhana)
        today=$(date +%s)
        exp_seconds=$(date -d "$exp_date_clean" +%s 2>/dev/null)
        
        if [[ $? -ne 0 ]]; then
            exp_color="${red}Invalid Date"
        elif [[ $exp_seconds -lt $today ]]; then
            exp_color="${red}$exp_date_clean (Expired)"
        elif [[ $(($exp_seconds - $today)) -lt 86400*7 ]]; then
            exp_color="${yellow}$exp_date_clean (Soon)"
        else
            exp_color="${green}$exp_date_clean"
        fi
        
        printf "${bold}${blue}│ ${green}%-4s${blue} │ ${cyan}%-20s ${blue}│ ${exp_color}%-20s${reset}${bold}${blue} │${reset}\n" \
               "$num" "$user_clean" "$exp_date_clean"
    done

    # Footer tabel
    echo "${bold}${blue}└─────┴──────────────────────┴──────────────────────┘${reset}"
    echo ""
fi

print_footer

exit 0
