import logging
import subprocess
import uuid 
import os   

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

# SSH States
SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT = map(chr, range(1, 5))

# VMESS States
VMESS_GET_USER, VMESS_GET_DURATION = map(chr, range(5, 7))

# VLESS States
VLESS_GET_USER, VLESS_GET_DURATION, VLESS_GET_IP_LIMIT, VLESS_GET_QUOTA = map(chr, range(7, 11))

# TROJAN States
TROJAN_GET_USER, TROJAN_GET_DURATION, TROJAN_GET_IP_LIMIT, TROJAN_GET_QUOTA = map(chr, range(11, 15))

# State untuk alur Renew SSH
RENEW_SSH_GET_USERNAME, RENEW_SSH_GET_DURATION = map(chr, range(15, 17))

# State untuk pembuatan akun Trial (terpisah per jenis)
TRIAL_CREATE_SSH, TRIAL_CREATE_VMESS, TRIAL_CREATE_VLESS, TRIAL_CREATE_TROJAN = map(chr, range(18, 22))

# State untuk penghapusan akun
DELETE_GET_USERNAME, DELETE_CONFIRMATION = map(chr, range(22, 24))

# State untuk alur list & view config VMESS
VMESS_SELECT_ACCOUNT = chr(25)

# State untuk alur list & view config SSH
SSH_SELECT_ACCOUNT = chr(26) 

# State baru untuk alur Renew VMESS
RENEW_VMESS_GET_USERNAME, RENEW_VMESS_GET_DURATION = map(chr, range(27, 29))
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
    target_message = update.callback_query.message if update.callback_query else update.message
    if target_message:
        if update.callback_query and target_message.text:
            await target_message.edit_text(
                "Please select from the menu below:",
                reply_markup=keyboards.get_main_menu_keyboard()
            )
        else:
            await update.effective_chat.send_message(
                "Please select from the menu below:",
                reply_markup=keyboards.get_main_menu_keyboard()
            )
    return ROUTE

async def handle_script_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    """Menangani kesalahan eksekusi script dan memberikan feedback ke pengguna."""
    msg = f"An unexpected error occurred: {error}"
    error_output = ""
    if isinstance(error, subprocess.CalledProcessError):
        error_output = error.stdout.strip() or error.stderr.strip()
        msg = error_output or "Script failed with a non-zero exit code but no error output."
    elif isinstance(error, FileNotFoundError):
        msg = f"Script file not found ({error}). Please check the path and permissions. Make sure it's in /opt/hokage-bot/"
    elif isinstance(error, TimeoutError):
        msg = "Script execution timed out. It took too long to respond."
    elif isinstance(error, ValueError) and "did not return a valid state" in str(error):
        msg = "Bot is currently in an unexpected state. Please use /cancel or /menu to reset."

    target_message = update.callback_query.message if update.callback_query else update.message

    if target_message:
        reply_markup = keyboards.get_back_to_menu_keyboard() if update.callback_query else keyboards.get_main_menu_keyboard()
        text_to_send = f"❌ **Operation Failed**\n\n**Reason:**\n`{msg}`"
        
        if update.callback_query and target_message.text:
            try:
                await target_message.edit_text(text_to_send, parse_mode='Markdown', reply_markup=reply_markup)
            except Exception:
                await update.effective_chat.send_message(text_to_send, parse_mode='Markdown', reply_markup=reply_markup)
        else:
            await target_message.reply_text(text_to_send, parse_mode='Markdown', reply_markup=reply_markup)

    logger.error(f"Script execution error: {msg}", exc_info=True)
    return ROUTE

async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Mengelola routing berdasarkan callback data dari keyboard."""
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
        await query.edit_message_text(f"➡️ Masukkan {raw_text}")
        return state

    if command == "ssh_renew":
        await query.edit_message_text(text="➡️ Silakan masukkan <b>username</b> akun SSH yang ingin diperpanjang:", parse_mode='HTML')
        return RENEW_SSH_GET_USERNAME
    elif command == "vmess_renew":
        await query.edit_message_text(text="➡️ Silakan masukkan <b>username</b> akun VMESS yang ingin diperpanjang:", parse_mode='HTML')
        return RENEW_VMESS_GET_USERNAME

    delete_starters = {
        "ssh_delete": ("SSH", DELETE_GET_USERNAME, "SSH username"),
        "vmess_delete": ("VMESS", DELETE_GET_USERNAME, "VMESS username"),
        "vless_delete": ("VLESS", DELETE_GET_USERNAME, "VLESS username"),
        "trojan_delete": ("TROJAN", DELETE_GET_USERNAME, "TROJAN username"),
    }
    
    if command in delete_starters:
        protocol, state, prompt_text = delete_starters[command]
        context.user_data['delete_protocol'] = protocol
        await query.edit_message_text(f"➡️ Masukkan <b>{prompt_text}</b> akun yang ingin dihapus:", parse_mode='HTML')
        return state

    trial_starters = {
        "ssh_trial": ("SSH", TRIAL_CREATE_SSH),
        "vmess_trial": ("VMESS", TRIAL_CREATE_VMESS), 
        "vless_trial": ("VLESS", TRIAL_CREATE_VLESS),
        "trojan_trial": ("TROJAN", TRIAL_CREATE_TROJAN),
    }
    
    if command in trial_starters:
        protocol_name, state = trial_starters[command]
        await query.edit_message_text(f"➡️ Masukkan durasi (hari) untuk akun Trial {protocol_name}:")
        return state

    if command == "ssh_list" or command == "ssh_config_user":
        await ssh_list_accounts(update, context) 
        return SSH_SELECT_ACCOUNT
    elif command == "vmess_list":
        await vmess_list_accounts(update, context)
        return VMESS_SELECT_ACCOUNT 
    elif command == "vless_list":
        await vless_list_accounts(update, context)
        return ROUTE
    elif command == "trojan_list":
        await trojan_list_accounts(update, context)
        return ROUTE
        
    if command == "menu_running":
        await run_script_and_reply(update, context, ['sudo', '/opt/hokage-bot/check_status_for_bot.sh'], "Status Layanan:")
        return ROUTE
    elif command == "menu_restart":
        await run_script_and_reply(update, context, ['sudo', '/opt/hokage-bot/restart_for_bot.sh'], "Restart Layanan:")
        return ROUTE
    elif command == "menu_backup":
        await run_script_and_reply(update, context, ['sudo', '/opt/hokage-bot/backup_for_bot.sh'], "Proses Backup:")
        return ROUTE
    elif command == "confirm_restore":
        context.user_data['action_to_confirm'] = 'restore'
        await query.edit_message_text(
            "⚠️ **PERINGATAN!**\n\nMelakukan restore akan menimpa konfigurasi yang ada.\n\nLanjutkan?",
            parse_mode='Markdown',
            reply_markup=keyboards.get_confirmation_keyboard()
        )
        return ROUTE 
    elif command == "reboot_server":
        context.user_data['action_to_confirm'] = 'reboot'
        await query.edit_message_text(
            "⚠️ **PERINGATAN!**\n\nServer akan reboot dan bot akan berhenti sementara. Lanjutkan?",
            parse_mode='Markdown',
            reply_markup=keyboards.get_confirmation_keyboard()
        )
        return ROUTE
    elif command == "trial_cleanup":
        await run_script_and_reply(update, context, ['sudo', '/opt/hokage-bot/trial_cleanup.sh'], "Trial Cleanup:")
        return ROUTE
    
    elif command in ["confirm_proceed", "cancel_action"]:
        action = context.user_data.pop('action_to_confirm', None)
        if command == "confirm_proceed":
            if action == 'restore':
                await run_script_and_reply(update, context, ['sudo', '/opt/hokage-bot/restore_for_bot.sh'], "Proses Restore:")
            elif action == 'reboot':
                await query.edit_message_text("⏳ Server akan reboot dalam beberapa detik...", reply_markup=keyboards.get_back_to_menu_keyboard())
                try:
                    subprocess.Popen(['sudo', 'reboot'])
                except Exception as e:
                    await handle_script_error(update, context, e)
            else:
                await query.edit_message_text("Aksi konfirmasi tidak dikenal atau sudah kadaluarsa.", reply_markup=keyboards.get_back_to_menu_keyboard())
        elif command == "cancel_action":
            await query.edit_message_text("Operasi dibatalkan.", reply_markup=keyboards.get_back_to_menu_keyboard())
        return ROUTE

    logger.warning(f"Unhandled callback query: {command} in route_handler.")
    await query.edit_message_text(f"Fitur {command} belum diimplementasikan atau tidak dikenal.", reply_markup=keyboards.get_back_to_menu_keyboard())
    return ROUTE

async def run_script_and_reply(update: Update, context: ContextTypes.DEFAULT_TYPE, script_command: list, success_message: str):
    target_message = update.callback_query.message if update.callback_query else update.message
    
    if update.callback_query:
        pass
    
    processing_text = "⏳ Sedang memproses, mohon tunggu..."
    if update.callback_query and target_message.text:
        try:
            await target_message.edit_text(processing_text)
        except Exception:
            await update.effective_chat.send_message(processing_text)
    else:
        await target_message.reply_text(processing_text)
        
    try:
        p = subprocess.run(script_command, capture_output=True, text=True, check=True, timeout=60)
        output = p.stdout.strip()
        if output:
            response_text = f"✅ **{success_message}**\n\n`{output}`"
        else:
            response_text = f"✅ **{success_message}**\n\nOperasi selesai, tidak ada output spesifik."
            
        if update.callback_query and target_message.text:
            try:
                await target_message.edit_text(response_text, parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())
            except Exception:
                await update.effective_chat.send_message(response_text, parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())
        else:
            await target_message.reply_text(response_text, parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())

    except Exception as e:
        await handle_script_error(update, context, e)

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
    if not update.message.text.isdigit() or int(update.message.text) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return SSH_GET_DURATION
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("➡️ Masukkan Limit IP:")
    return SSH_GET_IP_LIMIT

async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit() or int(update.message.text) < 1:
        await update.message.reply_text("❌ Limit IP harus berupa angka positif. Silakan coba lagi.")
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
    admin_telegram_id = update.effective_user.id
    
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return RENEW_SSH_GET_DURATION
    
    logger.info(f"Renewal Step 2: Duration: {duration} days for user: {username}")
    await update.message.reply_text("⏳ Sedang memproses perpanjangan, mohon tunggu...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_renew_ssh.sh', username, duration, str(admin_telegram_id)], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- VMESS Renew Handlers ---
async def renew_vmess_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    context.user_data['renew_username'] = username
    logger.info(f"VMESS Renewal Step 1: User {update.effective_user.id} entered username: {username}")
    await update.message.reply_text(
        f"✅ Username: <code>{username}</code>\n\n"
        "➡️ Sekarang, masukkan <b>durasi</b> perpanjangan (misal: 30 untuk 30 hari).",
        parse_mode='HTML'
    )
    return RENEW_VMESS_GET_DURATION

async def renew_vmess_get_duration_and_execute(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    username = context.user_data.get('renew_username')
    admin_telegram_id = update.effective_user.id
    
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return RENEW_VMESS_GET_DURATION
    
    logger.info(f"VMESS Renewal Step 2: Duration: {duration} days for user: {username}")
    await update.message.reply_text("⏳ Sedang memproses perpanjangan VMESS, mohon tunggu...")
    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_renew_vmess.sh', username, duration, str(admin_telegram_id)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- SSH List Accounts ---
async def ssh_list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/list_ssh_users.sh'], capture_output=True, text=True, check=True, timeout=30)
        script_output = p.stdout.strip()
    except Exception as e:
        await handle_script_error(update, context, e)
        return ROUTE

    if script_output == "NO_CLIENTS":
        await query.edit_message_text("ℹ️ *Belum ada akun SSH yang terdaftar di sistem.*", parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())
        return ROUTE
    
    account_details = []
    output_lines = script_output.splitlines()
    for line in output_lines:
        parts = line.split(' ', 2)
        if len(parts) == 3:
            account_details.append({
                'num': parts[0],
                'user': parts[1],
                'exp': parts[2]
            })
    
    context.user_data['ssh_accounts_list'] = account_details

    list_text = "📋 *DAFTAR AKUN SSH*\n"
    list_text += "---------------------------------------------------\n"
    list_text += "*No* | *Username* | *Expired (YYYY-MM-DD)*\n"
    list_text += "---------------------------------------------------\n"

    for acc in account_details:
        printf_user = "{:<18}".format(acc['user'])
        printf_exp = "{:<20}".format(acc['exp'])
        list_text += f"{acc['num']:<3} | `{printf_user}` | `{printf_exp}`\n"
    
    list_text += "---------------------------------------------------\n"
    list_text += f"📊 *Total:* `{len(account_details)}` akun.\n"
    list_text += "💡 *Tip:* Ketik nomor akun untuk melihat detail konfigurasi."
    list_text += "\n\nKetik `0` untuk kembali."

    await query.edit_message_text(list_text, parse_mode='Markdown')
    return SSH_SELECT_ACCOUNT

async def ssh_select_account_and_show_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    
    if user_input == '0':
        await update.message.reply_text("Dibatalkan, kembali ke menu utama.", reply_markup=keyboards.get_main_menu_keyboard())
        context.user_data.clear()
        return ROUTE

    if not user_input.isdigit():
        await update.message.reply_text("❌ Input tidak valid. Harap masukkan nomor akun yang valid atau `0` untuk kembali.")
        return SSH_SELECT_ACCOUNT

    selected_num = int(user_input)
    accounts_list = context.user_data.get('ssh_accounts_list')

    if not accounts_list or selected_num <= 0 or selected_num > len(accounts_list):
        await update.message.reply_text("❌ Nomor akun tidak valid. Harap pilih nomor dari daftar.", reply_markup=keyboards.get_back_to_menu_keyboard())
        return SSH_SELECT_ACCOUNT

    selected_account = accounts_list[selected_num - 1]
    username = selected_account['user']

    await update.message.reply_text(f"⏳ Mengambil konfigurasi untuk akun SSH `{username}`...", parse_mode='Markdown')

    try:
        config_log_path = f"/etc/xray/sshx/akun/log-create-{username}.log"
        
        if not os.path.exists(config_log_path):
            logger.error(f"Config log file not found for SSH user {username}: {config_log_path}")
            await update.message.reply_text(
                f"❌ File konfigurasi detail untuk akun SSH `{username}` tidak ditemukan di `{config_log_path}`.\n"
                "Harap buat akun ini ulang atau cek lokasi file log.", 
                parse_mode='Markdown', 
                reply_markup=keyboards.get_back_to_menu_keyboard()
            )
            context.user_data.clear()
            return ROUTE

        with open(config_log_path, 'r') as f:
            config_content = f.read()

        cleaned_config_content = subprocess.run(
            ['sed', 's/\x1B\[[0-9;]*m//g'], 
            input=config_content, 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        
        await update.message.reply_text(
            f"Berikut adalah detail konfigurasi untuk akun SSH `{username}`:\n\n"
            f"```\n{cleaned_config_content}\n```", 
            parse_mode='Markdown',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error showing SSH config for user {username}.", exc_info=True)
        await handle_script_error(update, context, e)
    
    context.user_data.clear()
    return ROUTE

# --- SSH Trial Handlers ---
async def start_ssh_trial_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("➡️ Masukkan durasi (hari) untuk akun Trial SSH:")
    return TRIAL_CREATE_SSH

async def create_ssh_trial_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return TRIAL_CREATE_SSH
    
    await update.message.reply_text("⏳ Membuat akun Trial SSH...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trial_ssh.sh', duration], capture_output=True, text=True, check=True, timeout=30)
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
    if not update.message.text.isdigit() or int(update.message.text) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return VMESS_GET_DURATION
    context.user_data['duration'] = update.message.text
    ud = context.user_data
    await update.message.reply_text("⏳ Membuat akun VMESS...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vmess_user.sh', ud['user'], ud['duration']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

async def vmess_list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/list_vmess_users.sh'], capture_output=True, text=True, check=True, timeout=30)
        script_output = p.stdout.strip()
    except Exception as e:
        await handle_script_error(update, context, e)
        return ROUTE

    if script_output == "NO_CLIENTS":
        await query.edit_message_text("ℹ️ *Belum ada akun VMESS yang terdaftar di sistem.*", parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())
        return ROUTE

    account_details = []
    output_lines = script_output.splitlines()
    for line in output_lines:
        parts = line.split(' ', 2)
        if len(parts) == 3:
            account_details.append({
                'num': parts[0],
                'user': parts[1],
                'exp': parts[2]
            })
    
    context.user_data['vmess_accounts_list'] = account_details

    list_text = "📋 *DAFTAR AKUN VMESS*\n"
    list_text += "---------------------------------------------------\n"
    list_text += "*No* | *Username* | *Expired (YYYY-MM-DD)*\n"
    list_text += "---------------------------------------------------\n"

    for acc in account_details:
        printf_user = "{:<18}".format(acc['user'])
        printf_exp = "{:<20}".format(acc['exp'])
        list_text += f"{acc['num']:<3} | `{printf_user}` | `{printf_exp}`\n"
    
    list_text += "---------------------------------------------------\n"
    list_text += f"📊 *Total:* `{len(account_details)}` akun.\n"
    list_text += "💡 *Tip:* Ketik nomor akun untuk melihat detail konfigurasi."
    list_text += "\n\nKetik `0` untuk kembali."

    await query.edit_message_text(list_text, parse_mode='Markdown')
    return VMESS_SELECT_ACCOUNT

async def vmess_select_account_and_show_config(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_input = update.message.text
    
    if user_input == '0':
        await update.message.reply_text("Dibatalkan, kembali ke menu utama.", reply_markup=keyboards.get_main_menu_keyboard())
        context.user_data.clear()
        return ROUTE

    if not user_input.isdigit():
        await update.message.reply_text("❌ Input tidak valid. Harap masukkan nomor akun yang valid atau `0` untuk kembali.")
        return VMESS_SELECT_ACCOUNT

    selected_num = int(user_input)
    accounts_list = context.user_data.get('vmess_accounts_list')

    if not accounts_list or selected_num <= 0 or selected_num > len(accounts_list):
        await update.message.reply_text("❌ Nomor akun tidak valid. Harap pilih nomor dari daftar.", reply_markup=keyboards.get_back_to_menu_keyboard())
        return VMESS_SELECT_ACCOUNT

    selected_account = accounts_list[selected_num - 1]
    username = selected_account['user']

    await update.message.reply_text(f"⏳ Mengambil konfigurasi untuk akun `{username}`...", parse_mode='Markdown')

    try:
        config_log_path = f"/etc/vmess/akun/vmess-{username}.log"
        
        if not os.path.exists(config_log_path):
            logger.error(f"Config log file not found for user {username}: {config_log_path}")
            await update.message.reply_text(
                f"❌ File konfigurasi detail untuk akun `{username}` tidak ditemukan di `{config_log_path}`.\n"
                "Harap buat akun ini ulang atau cek lokasi file log.", 
                parse_mode='Markdown', 
                reply_markup=keyboards.get_back_to_menu_keyboard()
            )
            context.user_data.clear()
            return ROUTE

        with open(config_log_path, 'r') as f:
            config_content = f.read()

        cleaned_config_content = subprocess.run(
            ['sed', 's/\x1B\[[0-9;]*m//g'], 
            input=config_content, 
            capture_output=True, 
            text=True, 
            check=True
        ).stdout.strip()
        
        await update.message.reply_text(
            f"Berikut adalah detail konfigurasi untuk akun `{username}`:\n\n"
            f"```\n{cleaned_config_content}\n```", 
            parse_mode='Markdown',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )

    except Exception as e:
        logger.error(f"Error showing config for user {username}.", exc_info=True)
        await handle_script_error(update, context, e)
    
    context.user_data.clear()
    return ROUTE

# --- VMESS Trial Handlers ---
async def start_vmess_trial_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("➡️ Masukkan durasi (hari) untuk akun Trial VMESS:")
    return TRIAL_CREATE_VMESS

async def create_vmess_trial_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return TRIAL_CREATE_VMESS

    await update.message.reply_text("⏳ Membuat akun Trial VMESS...")
    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_trial_vmess.sh', duration],
            capture_output=True, 
            text=True, 
            check=True, 
            timeout=30
        )
        
        output_lines = p.stdout.strip().split('\n')
        formatted_output = "\n".join(f"🔹 {line}" for line in output_lines)
        
        await update.message.reply_text(
            f"✅ <b>Akun Trial VMESS Berhasil Dibuat</b>\n\n"
            f"{formatted_output}\n\n"
            f"⏳ <i>Masa aktif: {duration} hari</i>",
            parse_mode='HTML',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() or "Gagal membuat akun trial (unknown error)"
        await update.message.reply_text(
            f"❌ <b>Gagal Membuat Akun Trial VMESS</b>\n\n"
            f"<code>{error_msg}</code>\n\n"
            "Silakan coba lagi atau hubungi admin.",
            parse_mode='HTML',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
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
    if not update.message.text.isdigit() or int(update.message.text) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return VLESS_GET_DURATION
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("➡️ Masukkan batas IP untuk akun VLESS:")
    return VLESS_GET_IP_LIMIT

async def vless_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit() or int(update.message.text) < 1:
        await update.message.reply_text("❌ Batas IP harus berupa angka positif. Silakan coba lagi.")
        return VLESS_GET_IP_LIMIT
    context.user_data['ip_limit'] = update.message.text
    await update.message.reply_text("➡️ Masukkan kuota GB untuk akun VLESS:")
    return VLESS_GET_QUOTA

async def vless_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit() or int(update.message.text) < 0:
        await update.message.reply_text("❌ Kuota GB harus berupa angka. Silakan coba lagi.")
        return VLESS_GET_QUOTA
    context.user_data['quota_gb'] = update.message.text
    await update.message.reply_text("⏳ Membuat akun VLESS...")
    ud = context.user_data
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vless_user.sh', ud['user'], ud['duration'], ud['ip_limit'], ud['quota_gb']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

async def vless_list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ Mengambil daftar akun VLESS...", reply_markup=keyboards.get_back_to_menu_keyboard())
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/list_vless_users.sh'], capture_output=True, text=True, check=True, timeout=30)
        await query.edit_message_text(f"📋 **Daftar Akun VLESS:**\n\n{p.stdout}", parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    return ROUTE

async def start_vless_trial_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("➡️ Masukkan durasi (hari) untuk akun Trial VLESS:")
    return TRIAL_CREATE_VLESS

async def create_vless_trial_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return TRIAL_CREATE_VLESS

    await update.message.reply_text("⏳ Membuat akun Trial VLESS...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trial_vless.sh', duration], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
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
    if not update.message.text.isdigit() or int(update.message.text) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return TROJAN_GET_DURATION
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("➡️ Masukkan batas IP untuk akun TROJAN:")
    return TROJAN_GET_IP_LIMIT

async def trojan_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit() or int(update.message.text) < 1:
        await update.message.reply_text("❌ Batas IP harus berupa angka positif. Silakan coba lagi.")
        return TROJAN_GET_IP_LIMIT
    context.user_data['ip_limit'] = update.message.text
    await update.message.reply_text("➡️ Masukkan kuota GB untuk akun TROJAN:")
    return TROJAN_GET_QUOTA

async def trojan_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if not update.message.text.isdigit() or int(update.message.text) < 0:
        await update.message.reply_text("❌ Kuota GB harus berupa angka. Silakan coba lagi.")
        return TROJAN_GET_QUOTA
    context.user_data['quota_gb'] = update.message.text
    await update.message.reply_text("⏳ Membuat akun TROJAN...")
    ud = context.user_data
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trojan_user.sh', ud['user'], ud['duration'], ud['ip_limit'], ud['quota_gb']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

async def trojan_list_accounts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("⏳ Mengambil daftar akun TROJAN...", reply_markup=keyboards.get_back_to_menu_keyboard())
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/list_trojan_users.sh'], capture_output=True, text=True, check=True, timeout=30)
        await query.edit_message_text(f"📋 **Daftar Akun TROJAN:**\n\n{p.stdout}", parse_mode='Markdown', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    return ROUTE

async def start_trojan_trial_creation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("➡️ Masukkan durasi (hari) untuk akun Trial TROJAN:")
    return TRIAL_CREATE_TROJAN

async def create_trojan_trial_account(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    duration = update.message.text
    if not duration.isdigit() or int(duration) <= 0:
        await update.message.reply_text("❌ Durasi harus berupa angka positif. Silakan coba lagi.")
        return TRIAL_CREATE_TROJAN

    await update.message.reply_text("⏳ Membuat akun Trial TROJAN...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trial_trojan.sh', duration], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- Delete Handlers ---
async def delete_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username_to_delete = update.message.text
    context.user_data['username_to_delete'] = username_to_delete

    protocol = context.user_data.get('delete_protocol', 'Akun')

    await update.message.reply_text(
        f"Anda yakin ingin menghapus akun {protocol} dengan username <b>{username_to_delete}</b>?",
        parse_mode='HTML',
        reply_markup=keyboards.get_confirmation_keyboard()
    )
    return DELETE_CONFIRMATION

async def delete_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    username_to_delete = context.user_data.get('username_to_delete')
    protocol = context.user_data.get('delete_protocol')

    if query.data == "confirm_proceed":
        if not username_to_delete or not protocol:
            logger.error("DEBUG_DELETE: Missing username_to_delete or protocol in context.user_data.")
            await query.edit_message_text("❌ Informasi akun tidak lengkap untuk dihapus. Operasi dibatalkan.", reply_markup=keyboards.get_back_to_menu_keyboard())
            context.user_data.clear()
            return ROUTE

        await query.edit_message_text(f"⏳ Sedang menghapus akun {protocol}...", reply_markup=keyboards.get_back_to_menu_keyboard())
        try:
            script_path = ''
            if protocol.lower() == 'ssh':
                script_path = '/opt/hokage-bot/delete-ssh.sh'
            elif protocol.lower() == 'vmess':
                script_path = '/opt/hokage-bot/delete_vmess_user.sh'
            elif protocol.lower() == 'vless':
                script_path = '/opt/hokage-bot/delete_vless_user.sh'
            elif protocol.lower() == 'trojan':
                script_path = '/opt/hokage-bot/delete_trojan_user.sh'
            else:
                logger.error(f"DEBUG_DELETE: Unknown protocol for delete: {protocol}")
                raise ValueError(f"Protokol {protocol} tidak didukung untuk penghapusan atau script tidak ditemukan.")

            logger.info(f"DEBUG_DELETE: Attempting to run script: {script_path} {username_to_delete}")
            p = subprocess.run(['sudo', script_path, username_to_delete], capture_output=True, text=True, check=True, timeout=30)
            await query.edit_message_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
        except Exception as e:
            logger.error(f"DEBUG_DELETE: Script execution failed for {protocol} delete.", exc_info=True)
            await handle_script_error(update, context, e)
    else:
        logger.info("DEBUG_DELETE: Delete operation cancelled by user.")
        await query.edit_message_text("Operasi penghapusan dibatalkan.", reply_markup=keyboards.get_back_to_menu_keyboard())

    context.user_data.clear()
    return ROUTE

# --- Conversation Control ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        context.user_data.clear()
    target_message = update.message if update.message else update.callback_query.message
    await update.effective_chat.send_message("❌ Operasi dibatalkan.", reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END

async def back_to_menu_from_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        context.user_data.clear()
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Dibatalkan, kembali ke menu utama.", reply_markup=keyboards.get_main_menu_keyboard())
    return ROUTE
