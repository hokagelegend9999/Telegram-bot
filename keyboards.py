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

# TAMBAHKAN FUNGSI BARU INI DI AKHIR FILE

def get_ssh_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard inline untuk menu panel SSH & VPN."""
    keyboard = [
        [InlineKeyboardButton("➕ Tambah Akun", callback_data="ssh_add"),
         InlineKeyboardButton("🟢 Cek User Online", callback_data="ssh_online")],

        [InlineKeyboardButton("🎁 Akun Trial", callback_data="ssh_trial"),
         InlineKeyboardButton("📄 Cek Konfigurasi", callback_data="ssh_config")],

        [InlineKeyboardButton("🔄 Perpanjang Akun", callback_data="ssh_renew"),
         InlineKeyboardButton("🔀 Ubah Limit IP", callback_data="ssh_limit")],

        [InlineKeyboardButton("🗑️ Hapus Akun", callback_data="ssh_delete"),
         InlineKeyboardButton("🔒 Kunci Login", callback_data="ssh_lock")],

        # Tombol di baris sendiri agar lebih jelas
        [InlineKeyboardButton("🔓 Buka Kunci Login", callback_data="ssh_unlock")],

        # Tombol untuk kembali ke menu utama
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_to_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
