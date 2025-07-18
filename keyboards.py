# File: keyboards.py
# Versi baru dengan ikon yang lebih menarik.

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard inline dengan ikon yang relevan dan menarik."""
    keyboard = [
        # Baris 1: Layanan Utama
        [InlineKeyboardButton("🌐 SSH & VPN", callback_data="menu_ssh"),
         InlineKeyboardButton("🚀 VMESS", callback_data="menu_vmess")],
        
        # Baris 2: Layanan Tambahan
        [InlineKeyboardButton("⚡ VLESS", callback_data="menu_vless"),
         InlineKeyboardButton("🐴 TROJAN", callback_data="menu_trojan")],
        
        # Baris 3: Manajemen Sistem
        [InlineKeyboardButton("🟢 Cek Status", callback_data="menu_running"),
         InlineKeyboardButton("🔄 Restart Layanan", callback_data="menu_restart")],

        # Baris 4: Utilitas
        [InlineKeyboardButton("📥 Update Skrip", callback_data="menu_update"),
         InlineKeyboardButton("📦 Backup", callback_data="menu_backup")],

        # Baris 5: Pengaturan & Reboot
        [InlineKeyboardButton("⚙️ Setting", callback_data="menu_setting"),
         InlineKeyboardButton("🔌 Reboot Server", callback_data="menu_reboot")],
        
        # Baris 6: Tombol Penutup
        [InlineKeyboardButton("❌ Tutup Menu ❌", callback_data="close_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
