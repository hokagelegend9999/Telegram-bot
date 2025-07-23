from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🌐 SSH/VPN", callback_data="menu_ssh")],
        [InlineKeyboardButton("🚀 VMESS", callback_data="menu_vmess")],
        [InlineKeyboardButton("⚡ VLESS", callback_data="menu_vless")],
        [InlineKeyboardButton("🐴 TROJAN", callback_data="menu_trojan")],
        [InlineKeyboardButton("🔧 Server Tools", callback_data="menu_tools")], # Tombol Tools
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

def get_vmess_menu_keyboard() -> InlineKeyboardMarkup: # <-- Baru
    keyboard = [
        [InlineKeyboardButton("➕ Buat Akun Baru", callback_data="vmess_add")],
        [InlineKeyboardButton("🎁 Akun Trial", callback_data="vmess_trial")],
        [InlineKeyboardButton("🗑️ Hapus Akun", callback_data="vmess_delete")],
        [InlineKeyboardButton("📋 List Akun", callback_data="vmess_list")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_vless_menu_keyboard() -> InlineKeyboardMarkup: # <-- Baru
    keyboard = [
        [InlineKeyboardButton("➕ Buat Akun Baru", callback_data="vless_add")],
        [InlineKeyboardButton("🎁 Akun Trial", callback_data="vless_trial")],
        [InlineKeyboardButton("🗑️ Hapus Akun", callback_data="vless_delete")],
        [InlineKeyboardButton("📋 List Akun", callback_data="vless_list")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_trojan_menu_keyboard() -> InlineKeyboardMarkup: # <-- Baru
    keyboard = [
        [InlineKeyboardButton("➕ Buat Akun Baru", callback_data="trojan_add")],
        [InlineKeyboardButton("🎁 Akun Trial", callback_data="trojan_trial")],
        [InlineKeyboardButton("🗑️ Hapus Akun", callback_data="trojan_delete")],
        [InlineKeyboardButton("📋 List Akun", callback_data="trojan_list")],
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_tools_menu_keyboard() -> InlineKeyboardMarkup: # <-- Baru
    keyboard = [
        [InlineKeyboardButton("🟢 Cek Status", callback_data="menu_running")], # Pakai check_status_for_bot.sh
        [InlineKeyboardButton("🔄 Restart Layanan", callback_data="menu_restart")], # Pakai restart_for_bot.sh
        [InlineKeyboardButton("☁️ Backup", callback_data="menu_backup")], # Pakai backup_for_bot.sh
        [InlineKeyboardButton("⬇️ Restore", callback_data="confirm_restore")], # Pakai restore_for_bot.sh
        [InlineKeyboardButton("🗑️ Trial Cleanup", callback_data="trial_cleanup")], # Pakai trial_cleanup.sh
        [InlineKeyboardButton("🔄 Reboot Server", callback_data="reboot_server")], # Perlu implementasi handler untuk ini
        [InlineKeyboardButton("⬅️ Kembali", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_renew_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = [
        [InlineKeyboardButton("🔐 Renew SSH", callback_data="renew_ssh")],
        [InlineKeyboardButton("🔒 Renew VPN", callback_data="renew_vpn")],
        [InlineKeyboardButton("🔄 Renew All", callback_data="renew_all")],
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
