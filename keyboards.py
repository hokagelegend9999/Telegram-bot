# File: keyboards.py
# Versi baru dengan nama keyboard yang lebih jelas.

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard inline untuk menu utama."""
    keyboard = [
        [InlineKeyboardButton("🌐 SSH & VPN", callback_data="menu_ssh"),
         InlineKeyboardButton("🚀 VMESS", callback_data="menu_vmess")],
        [InlineKeyboardButton("⚡ VLESS", callback_data="menu_vless"),
         InlineKeyboardButton("🐴 TROJAN", callback_data="menu_trojan")],
        [InlineKeyboardButton("🟢 Cek Status", callback_data="menu_running"),
         InlineKeyboardButton("🔄 Restart Layanan", callback_data="menu_restart")],
        [InlineKeyboardButton("📥 Update Skrip", callback_data="menu_update"),
         InlineKeyboardButton("📦 Backup", callback_data="menu_backup")],
        [InlineKeyboardButton("⚙️ Setting", callback_data="menu_setting"),
         InlineKeyboardButton("🔌 Reboot Server", callback_data="menu_reboot")],
        [InlineKeyboardButton("❌ Tutup Menu ❌", callback_data="close_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

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
        [InlineKeyboardButton("🔓 Buka Kunci Login", callback_data="ssh_unlock")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_to_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- NAMA FUNGSI DIPERBARUI ---
def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard dengan satu tombol untuk kembali ke menu utama."""
    keyboard = [
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
