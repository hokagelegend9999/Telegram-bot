from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🌐 SSH/VPN", callback_data="menu_ssh")],
        [InlineKeyboardButton("🚀 VMESS", callback_data="menu_vmess")],
        [InlineKeyboardButton("⚡ VLESS", callback_data="menu_vless")],
        [InlineKeyboardButton("🐴 TROJAN", callback_data="menu_trojan")],
        [InlineKeyboardButton("🔧 Server Tools", callback_data="menu_tools")],
        [InlineKeyboardButton("❌ Tutup Menu", callback_data="close_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_ssh_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("➕ Buat Akun Baru", callback_data="ssh_add")],
        [InlineKeyboardButton("🔄 Perpanjang Akun", callback_data="ssh_renew")],
        [InlineKeyboardButton("🎁 Akun Trial", callback_data="ssh_trial")],
        [InlineKeyboardButton("🗑️ Hapus Akun", callback_data="ssh_delete")],
        [InlineKeyboardButton("📋 List Akun", callback_data="ssh_list")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_renew_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔐 Renew SSH", callback_data="renew_ssh")],
        [InlineKeyboardButton("🔒 Renew VPN", callback_data="renew_vpn")],
        [InlineKeyboardButton("🔄 Renew Both", callback_data="renew_both")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="menu_ssh")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_back_to_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("⬅️ Kembali ke Menu", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_confirmation_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("✅ Ya, Lanjutkan", callback_data="confirm_proceed")],
        [InlineKeyboardButton("❌ Batal", callback_data="cancel_action")]
    ]
    return InlineKeyboardMarkup(keyboard)
