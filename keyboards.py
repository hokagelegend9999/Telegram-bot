# keyboards.py
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Membuat keyboard inline 2 kolom untuk menu utama."""
    keyboard = [
        [InlineKeyboardButton("[01] SSH VPN", callback_data="menu_ssh"),
         InlineKeyboardButton("[06] RUNNING", callback_data="menu_running")],
        [InlineKeyboardButton("[02] VMESS", callback_data="menu_vmess"),
         InlineKeyboardButton("[07] RESTART", callback_data="menu_restart")],
        [InlineKeyboardButton("[03] VLESS", callback_data="menu_vless"),
         InlineKeyboardButton("[08] REBOOT", callback_data="menu_reboot")],
        [InlineKeyboardButton("[04] TROJAN", callback_data="menu_trojan"),
         InlineKeyboardButton("[09] UPDATE", callback_data="menu_update")],
        [InlineKeyboardButton("[05] BACKUP", callback_data="menu_backup"),
         InlineKeyboardButton("[10] SETTING", callback_data="menu_setting")],
        [InlineKeyboardButton("Tutup Menu", callback_data="close_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)
