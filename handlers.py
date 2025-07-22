# /opt/hokage-bot/handlers.py

import logging
import subprocess
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler,
    CommandHandler
)
import keyboards
import config
import database

logger = logging.getLogger(__name__)

# --- Definisi State (LENGKAP) ---
ROUTE = chr(0)
SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT = map(chr, range(1, 5))
VMESS_GET_USER, VMESS_GET_DURATION = map(chr, range(5, 7))
VLESS_GET_USER, VLESS_GET_DURATION, VLESS_GET_IP_LIMIT, VLESS_GET_QUOTA = map(chr, range(7, 11))
TROJAN_GET_USER, TROJAN_GET_DURATION, TROJAN_GET_IP_LIMIT, TROJAN_GET_QUOTA = map(chr, range(11, 15))

# State baru untuk alur Renew SSH (yang sudah disederhanakan)
RENEW_SSH_GET_USERNAME, RENEW_SSH_GET_DURATION = map(chr, range(15, 17))

TRIAL_CREATE_SSH, TRIAL_CREATE_VMESS, TRIAL_CREATE_VLESS, TRIAL_CREATE_TROJAN = map(chr, range(18, 22))
DELETE_GET_USERNAME, DELETE_CONFIRMATION = map(chr, range(22, 24))
# --- Akhir Definisi State ---


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mengirim pesan selamat datang dan menu utama."""
    user = update.effective_user
    database.add_user_if_not_exists(user.id, user.first_name, user.username)
    await update.message.reply_text(
        "🤖 Welcome to SSH/VPN Management Bot!\n\n"
        "Use /menu to access all features.",
        reply_markup=keyboards.get_main_menu_keyboard()
    )
    return ROUTE

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menampilkan menu utama."""
    await update.message.reply_text(
        "Please select from the menu below:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )
    return ROUTE

async def handle_script_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    msg = f"An unexpected error occurred: {error}"
    if isinstance(error, subprocess.CalledProcessError):
        error_output_from_script = error.stdout.strip() or error.stderr.strip()
        msg = error_output_from_script or "Script failed with a non-zero exit code but no error output."
    elif isinstance(error, FileNotFoundError):
        msg = "Script file not found. Please check the path and permissions."

    target_message = update.callback_query.message if update.callback_query else update.message

    if target_message:
        reply_markup = keyboards.get_back_to_menu_keyboard() if update.callback_query else keyboards.get_main_menu_keyboard()
        text_to_send = f"❌ **Operation Failed**\n\n**Reason:**\n`{msg}`"
        
        if update.callback_query:
            await target_message.edit_text(text_to_send, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await target_message.reply_text(text_to_send, parse_mode='Markdown', reply_markup=reply_markup)

    logger.error(f"Script execution error: {msg}", exc_info=True)
    return ROUTE

async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = update.effective_user.id

    logger.info(f"User {user_id} selected callback: {command}")

    if command in ["main_menu", "back_to_main_menu"]:
        await query.edit_message_text("Main Menu:", reply_markup=keyboards.get_main_menu_keyboard())
        return ROUTE

    menu_map = {
        "menu_ssh": ("SSH", keyboards.get_ssh_menu_keyboard()),
        "menu_vmess": ("VMESS", keyboards.get_vmess_menu_keyboard()),
        "menu_vless": ("VLESS", keyboards.get_vless_menu_keyboard()),
        "menu_trojan": ("TROJAN", keyboards.get_trojan_menu_keyboard()),
        "menu_tools": ("TOOLS", keyboards.get_tools_menu_keyboard())
    }
    if command in menu_map:
        menu_name, keyboard = menu_map[command]
        await query.edit_message_text(f"{menu_name} PANEL MENU", reply_markup=keyboard)
        return ROUTE

    conv_starters = {
        "ssh_add": ("SSH Username:", SSH_GET_USERNAME),
        "vmess_add": ("VMESS Username:", VMESS_GET_USER),
        "vless_add": ("VLESS Username:", VLESS_GET_USER),
        "trojan_add": ("Trojan Username:", TROJAN_GET_USER)
    }
    if command in conv_starters:
        raw_text, state = conv_starters[command]
        await query.edit_message_text(f"➡️ {raw_text}")
        return state

    if command == "ssh_renew":
        await query.edit_message_text(text="➡️ Silakan masukkan <b>username</b> akun SSH yang ingin diperpanjang:", parse_mode='HTML')
        return RENEW_SSH_GET_USERNAME

    # (Sisa logika dari file asli Anda untuk list, trial, delete, tools, dll.)
    # ... Anda bisa tambahkan kembali logika tersebut di sini jika diperlukan ...

    logger.warning(f"Unhandled callback query: {command} in route_handler.")
    await query.edit_message_text(f"Fitur {command} belum diimplementasikan.", reply_markup=keyboards.get_back_to_menu_keyboard())
    return ROUTE

# --- SSH Renewal Handlers (BARU & SEDERHANA) ---
async def renew_ssh_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    context.user_data['renew_username'] = username
    logger.info(f"Renewal Step 1: User {update.effective_user.id} entered username: {username}")
    await update.message.reply_text(
        f"✅ Username: <code>{username}</code>\n\n"
        "➡️ Sekarang, masukkan <b>durasi</b> perpanjangan (misal: 30 untuk 30 hari).",
        parse_mode='HTML'
    )
    return RENEW_SSH_GET_DURATION

async def renew_ssh_get_duration_and_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    username = context.user_data.get('renew_username')
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return RENEW_SSH_GET_DURATION
    logger.info(f"Renewal Step 2: Duration: {duration} days for user: {username}")
    await update.message.reply_text("⏳ Sedang memproses perpanjangan, mohon tunggu...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/renew-ssh.sh', username, duration], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- SSH Creation Handlers ---
async def ssh_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text("➡️ Masukkan Password:")
    return SSH_GET_PASSWORD

async def ssh_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['password'] = update.message.text
    await update.message.reply_text("➡️ Masukkan Durasi (hari):")
    return SSH_GET_DURATION

async def ssh_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Durasi harus berupa angka. Silakan coba lagi.")
        return SSH_GET_DURATION
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("➡️ Masukkan Limit IP:")
    return SSH_GET_IP_LIMIT

async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Limit IP harus berupa angka. Silakan coba lagi.")
        return SSH_GET_IP_LIMIT
    context.user_data['ip_limit'] = update.message.text
    await update.message.reply_text("⏳ Membuat akun SSH...")
    ud = context.user_data
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_ssh.sh', ud['username'], ud['password'], ud['duration'], ud['ip_limit']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- VMESS Handlers ---
async def vmess_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text
    await update.message.reply_text("➡️ Masukkan Durasi (hari):")
    return VMESS_GET_DURATION

async def vmess_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    ud = context.user_data
    await update.message.reply_text("⏳ Membuat akun VMESS...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vmess_user.sh', ud['user'], ud['duration']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- VLESS Handlers ---
async def vless_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text
    await update.message.reply_text("➡️ Masukkan durasi akun VLESS (hari):")
    return VLESS_GET_DURATION

async def vless_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("➡️ Masukkan batas IP untuk akun VLESS:")
    return VLESS_GET_IP_LIMIT

async def vless_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Batas IP harus berupa angka. Silakan coba lagi.")
        return VLESS_GET_IP_LIMIT
    context.user_data['ip_limit'] = update.message.text
    await update.message.reply_text("➡️ Masukkan kuota GB untuk akun VLESS:")
    return VLESS_GET_QUOTA

async def vless_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Kuota GB harus berupa angka. Silakan coba lagi.")
        return VLESS_GET_QUOTA
    context.user_data['quota_gb'] = update.message.text
    await update.message.reply_text("⏳ Membuat akun VLESS...")
    ud = context.user_data
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vless_user.sh', ud['user'], ud['duration'], ud['ip_limit'], ud['quota_gb']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- TROJAN Handlers ---
async def trojan_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text
    await update.message.reply_text("➡️ Masukkan durasi akun TROJAN (hari):")
    return TROJAN_GET_DURATION

async def trojan_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("➡️ Masukkan batas IP untuk akun TROJAN:")
    return TROJAN_GET_IP_LIMIT

async def trojan_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Batas IP harus berupa angka. Silakan coba lagi.")
        return TROJAN_GET_IP_LIMIT
    context.user_data['ip_limit'] = update.message.text
    await update.message.reply_text("➡️ Masukkan kuota GB untuk akun TROJAN:")
    return TROJAN_GET_QUOTA

async def trojan_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit():
        await update.message.reply_text("❌ Kuota GB harus berupa angka. Silakan coba lagi.")
        return TROJAN_GET_QUOTA
    context.user_data['quota_gb'] = update.message.text
    await update.message.reply_text("⏳ Membuat akun TROJAN...")
    ud = context.user_data
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trojan_user.sh', ud['user'], ud['duration'], ud['ip_limit'], ud['quota_gb']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- Conversation Control ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        context.user_data.clear()
    await update.message.reply_text("❌ Operasi dibatalkan.", reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END

async def back_to_menu_from_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        context.user_data.clear()
    await update.message.reply_text("Dibatalkan, kembali ke menu utama.")
    return await menu(update, context)
