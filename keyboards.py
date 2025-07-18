# File: keyboards.py
# Versi baru dengan sub-menu Vmess

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
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
    keyboard = [
        [InlineKeyboardButton("➕ Tambah Akun", callback_data="ssh_add"),
         InlineKeyboardButton("🎁 Akun Trial", callback_data="ssh_trial")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_to_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

# --- FUNGSI BARU ---
def get_vmess_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard inline untuk menu panel Vmess."""
    keyboard = [
        [InlineKeyboardButton("➕ Tambah Akun", callback_data="vmess_add")],
        [InlineKeyboardButton("🎁 Akun Trial", callback_data="vmess_trial")],
        [InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data="back_to_main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="back_to_main_menu")]]
    return InlineKeyboardMarkup(keyboard)
