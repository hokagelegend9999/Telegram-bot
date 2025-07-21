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

# --- Definisi State (PASTIKAN UNIK dan TIDAK TUMPANG TINDIH) ---
ROUTE = chr(0)
SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT = map(chr, range(1, 5))
VMESS_GET_USER, VMESS_GET_DURATION = map(chr, range(5, 7))
VLESS_GET_USER, VLESS_GET_DURATION, VLESS_GET_IP_LIMIT, VLESS_GET_QUOTA = map(chr, range(7, 11))
TROJAN_GET_USER, TROJAN_GET_DURATION, TROJAN_GET_IP_LIMIT, TROJAN_GET_QUOTA = map(chr, range(11, 15))

RENEW_GET_USERNAME, RENEW_SELECT_TYPE, RENEW_CONFIRMATION = map(chr, range(15, 18))

TRIAL_CREATE_SSH, TRIAL_CREATE_VMESS, TRIAL_CREATE_VLESS, TRIAL_CREATE_TROJAN = map(chr, range(18, 22))

# State baru untuk alur Delete
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

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        await update.message.reply_text("This command is for admins only.")
        return
    await update.message.reply_text("Welcome to Admin Panel.")

async def handle_script_error(update: Update, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    msg = f"Error occurred: {error}"
    if isinstance(error, subprocess.CalledProcessError):
        msg = error.stdout.strip() or error.stderr.strip() or "Script failed without error output."

    target_message = update.callback_query.message if update.callback_query else update.message
    
    if target_message:
        if update.callback_query:
            await target_message.edit_text( 
                f"❌ Failed:\n{msg}", # Plain text
                reply_markup=keyboards.get_back_to_menu_keyboard()
            )
        else:
            await target_message.reply_text(
                f"❌ Failed:\n{msg}", # Plain text
                reply_markup=keyboards.get_main_menu_keyboard()
            )
    
    logger.error(f"Script execution error: {msg}", exc_info=True)
    return ROUTE

async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    command = query.data
    user_id = update.effective_user.id

    logger.info(f"User {user_id} selected callback: {command}")

    if command in ["main_menu", "back_to_main_menu"]:
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        return ROUTE
    
    if command in ["menu_ssh", "menu_vmess", "menu_vless", "menu_trojan", "menu_tools"]:
        menu_name = command.split('_')[1].upper()
        
        keyboard_to_send = keyboards.get_back_to_menu_keyboard()

        if menu_name == "SSH":
            keyboard_to_send = keyboards.get_ssh_menu_keyboard()
            logger.info(f"DEBUG: SSH Menu Keyboard being sent: {keyboard_to_send.to_dict()}")
        elif menu_name == "VMESS":
            keyboard_to_send = keyboards.get_vmess_menu_keyboard()
            logger.info(f"DEBUG: VMESS Menu Keyboard being sent: {keyboard_to_send.to_dict()}")
        elif menu_name == "VLESS":
            keyboard_to_send = keyboards.get_vless_menu_keyboard()
            logger.info(f"DEBUG: VLESS Menu Keyboard being sent: {keyboard_to_send.to_dict()}")
        elif menu_name == "TROJAN":
            keyboard_to_send = keyboards.get_trojan_menu_keyboard()
            logger.info(f"DEBUG: TROJAN Menu Keyboard being sent: {keyboard_to_send.to_dict()}")
        elif menu_name == "TOOLS":
            keyboard_to_send = keyboards.get_tools_menu_keyboard()
            logger.info(f"DEBUG: TOOLS Menu Keyboard being sent: {keyboard_to_send.to_dict()}")

        await query.edit_message_text(
            f"{menu_name} PANEL MENU", 
            reply_markup=keyboard_to_send
        )
        return ROUTE

    # --- Memulai Alur Conversational (Add) ---
    conv_starters = {
        "ssh_add": ("SSH Username:", SSH_GET_USERNAME),
        "vmess_add": ("VMESS Username:", VMESS_GET_USER),
        "vless_add": ("VLESS Username:", VLESS_GET_USER),
        "trojan_add": ("Trojan Username:", TROJAN_GET_USER)
    }
    if command in conv_starters:
        raw_text, state = conv_starters[command]
        await query.edit_message_text(f"{raw_text}")
        return state

    # --- Alur Trial (BARU: Langsung eksekusi script tanpa minta username) ---
    trial_script_map = {
        "trial_start_ssh": {"script": "create_trial_ssh.sh", "parse_mode": None}, 
        "trial_start_vmess": {"script": "create_trial_vmess.sh", "parse_mode": None}, 
        "trial_start_vless": {"script": "create_trial_vless.sh", "parse_mode": None}, 
        "trial_start_trojan": {"script": "create_trial_trojan.sh", "parse_mode": 'MarkdownV2'} 
    }

    if command in trial_script_map:
        trial_config = trial_script_map[command]
        script_to_run = trial_config["script"]
        parse_mode_for_output = trial_config["parse_mode"]
        
        trial_type = command.replace("trial_start_", "").upper()
        
        await query.edit_message_text(f"⏳ Creating {trial_type} trial account...")
        try:
            p = subprocess.run(
                ['sudo', f'/opt/hokage-bot/{script_to_run}'], # TANPA ARGUMEN USER
                capture_output=True,
                text=True,
                check=True,
                timeout=60 
            )
            await query.message.reply_text( 
                f"✅ {trial_type} Trial Result:\n{p.stdout}",
                parse_mode=parse_mode_for_output, 
                reply_markup=keyboards.get_back_to_menu_keyboard()
            )
        except Exception as e:
            return await handle_script_error(update, context, e) 
        return ROUTE 

    # Alur Perpanjangan SSH
    if command == "ssh_renew":
        await query.edit_message_text(text="Silakan masukkan username akun yang ingin diperpanjang:")
        return RENEW_GET_USERNAME

    # --- Fitur List Akun ---
    if command == "ssh_list":
        await query.edit_message_text("⏳ Mengambil daftar akun SSH Anda...")
        try:
            account_list_text = await database.get_ssh_account_list(user_id)
            
            await query.edit_message_text(
                f"📋 Daftar Akun SSH Anda:\n\n{account_list_text}", 
                reply_markup=keyboards.get_ssh_menu_keyboard() 
            )
        except Exception as e:
            logger.error(f"Error fetching SSH account list for user {user_id}: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ Gagal mengambil daftar akun SSH. Mohon coba lagi nanti.\n{str(e)}", 
                reply_markup=keyboards.get_ssh_menu_keyboard()
            )
        return ROUTE
    
    if command == "vmess_list":
        await query.edit_message_text("⏳ Mengambil daftar akun VMESS Anda...")
        try:
            account_list_text = await database.get_vmess_account_list(user_id) 
            
            await query.edit_message_text(
                f"📋 Daftar Akun VMESS Anda:\n\n{account_list_text}", 
                reply_markup=keyboards.get_vmess_menu_keyboard() 
            )
        except Exception as e:
            logger.error(f"Error fetching VMESS account list for user {user_id}: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ Gagal mengambil daftar akun VMESS. Mohon coba lagi nanti.\n{str(e)}", 
                reply_markup=keyboards.get_vmess_menu_keyboard()
            )
        return ROUTE

    if command == "vless_list": # Ini adalah blok yang harus terpicu
        await query.edit_message_text("⏳ Mengambil daftar akun VLESS Anda...")
        try:
            account_list_text = await database.get_vless_account_list(user_id) 
            
            await query.edit_message_text(
                f"📋 Daftar Akun VLESS Anda:\n\n{account_list_text}", 
                reply_markup=keyboards.get_vless_menu_keyboard() 
            )
        except Exception as e:
            logger.error(f"Error fetching VLESS account list for user {user_id}: {e}", exc_info=True)
            await query.edit_message_text(
                f"❌ Gagal mengambil daftar akun VLESS. Mohon coba lagi nanti.\n{str(e)}", 
                reply_markup=keyboards.get_vless_menu_keyboard()
            )
        return ROUTE

    # --- Memulai Alur Delete Akun (BARU) ---
    # Diarahkan dari tombol "🗑️ Hapus Akun" di SSH/VMESS/VLESS/TROJAN menu
    delete_starter_map = {
        "ssh_delete": "SSH",
        "vmess_delete": "VMESS",
        "vless_delete": "VLESS",
        "trojan_delete": "TROJAN"
    }
    if command in delete_starter_map:
        account_type = delete_starter_map[command]
        context.user_data['delete_type'] = account_type # Simpan jenis akun yang akan dihapus
        await query.edit_message_text(f"Silakan masukkan username akun {account_type} yang ingin dihapus:")
        return DELETE_GET_USERNAME # Transisi ke state untuk mendapatkan username

    # --- Script Execution Commands (Selain Trial yang kini punya alur sendiri) ---
    script_map = {
        "menu_restart": "restart_for_bot.sh",
        "menu_running": "check_status_for_bot.sh",
        "menu_backup": "backup_for_bot.sh",
        "confirm_restore": "restore_for_bot.sh",
        "trial_cleanup": "trial_cleanup.sh", 
        "reboot_server": "reboot_server.sh" 
    }

    if command in script_map:
        wait_message = f"⏳ Processing {command.replace('_', ' ').title()}..."
        timeout = 120
        if command in ["confirm_restore", "menu_backup", "reboot_server"]:
            wait_message = f"⚙️ Starting {command.replace('menu_', '')} process...\n\nThis may take several minutes."
            timeout = 300
        
        if command == "reboot_server":
            await query.edit_message_text("🚨 Server akan me-reboot dalam beberapa detik!\nBot akan offline sementara.")
            subprocess.Popen(['sudo', f'/opt/hokage-bot/{script_map[command]}']) 
            return ConversationHandler.END 
            
        await query.edit_message_text(wait_message)
        try:
            p = subprocess.run(
                ['sudo', f'/opt/hokage-bot/{script_map[command]}'],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            await query.edit_message_text( 
                f"✅ Result:\n{p.stdout}", 
                reply_markup=keyboards.get_back_to_menu_keyboard()
            )
        except Exception as e:
            return await handle_script_error(update, context, e) 

        return ROUTE

    # --- Penutup Menu ---
    if command == "close_menu":
        await query.edit_message_text("Menu closed.")
        return ConversationHandler.END

    # Default Fallback untuk Callback Query yang tidak tertangani
    await query.edit_message_text(
        f"Fitur {command} belum siap.", 
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )
    logger.warning(f"Unhandled callback query: {command} in route_handler.")
    return ROUTE

# --- SSH Renewal Handlers ---
async def renew_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    context.user_data['renew_username'] = username
    logger.info(f"User {update.effective_user.id} entered username for renewal: {username}")

    await update.message.reply_text(
        f"Anda ingin memperpanjang akun '{username}'. Pilih jenis perpanjangan:",
        reply_markup=keyboards.get_renew_menu_keyboard()
    )
    return RENEW_SELECT_TYPE

async def renew_select_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    renew_type = query.data
    username = context.user_data.get('renew_username')
    logger.info(f"User {update.effective_user.id} selected renewal type: {renew_type} for username: {username}")

    if not username:
        await query.edit_message_text("Terjadi kesalahan: informasi perpanjangan tidak lengkap. Silakan mulai ulang proses perpanjangan.")
        return ConversationHandler.END

    context.user_data['selected_renew_type'] = renew_type

    confirmation_text = f"Anda akan memperpanjang akun '{username}' untuk layanan "
    if renew_type == "renew_ssh":
        confirmation_text += "SSH."
    elif renew_type == "renew_vpn":
        confirmation_text += "VPN."
    elif renew_type == "renew_all":
        confirmation_text += "SSH dan VPN."

    confirmation_text += "\n\nApakah Anda yakin ingin melanjutkan?"

    await query.edit_message_text(text=confirmation_text, reply_markup=keyboards.get_confirmation_keyboard())
    return RENEW_CONFIRMATION

async def renew_confirm_proceed(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()

    username = context.user_data.get('renew_username')
    renew_type = context.user_data.get('selected_renew_type')
    user_id = update.effective_user.id
    logger.info(f"User {user_id} confirmed renewal for {username}, type {renew_type}")

    if not username or not renew_type:
        await query.edit_message_text("Terjadi kesalahan: informasi perpanjangan tidak lengkap. Silakan coba lagi.")
        return ConversationHandler.END

    await query.edit_message_text(f"Memproses perpanjangan akun '{username}' untuk {renew_type.replace('renew_', '').upper()}...")

    script_to_run = ""
    if renew_type == "renew_ssh":
        script_to_run = "create_renew_ssh.sh" 
    elif renew_type == "renew_vpn":
        script_to_run = "renew_vpn.sh" 
    elif renew_type == "renew_all":
        script_to_run = "renew_all.sh" 
        
    if script_to_run:
        try:
            p = subprocess.run(
                ['sudo', f'/opt/hokage-bot/{script_to_run}', username, renew_type, str(user_id)],
                capture_output=True,
                text=True,
                check=True,
                timeout=60 
            )
            await query.message.reply_text( 
                f"✅ Perpanjangan akun '{username}' untuk {renew_type.replace('renew_', '').upper()} berhasil!\n{p.stdout}",
                reply_markup=keyboards.get_main_menu_keyboard()
            )
        except Exception as e:
            await handle_script_error(update, context, e) 
    else:
        await query.message.reply_text("Logika perpanjangan untuk jenis ini belum diimplementasikan.", reply_markup=keyboards.get_main_menu_keyboard())

    context.user_data.pop('renew_username', None)
    context.user_data.pop('selected_renew_type', None)
    context.user_data.pop('current_action', None)

    await query.message.reply_text("Silakan pilih menu lainnya:", reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END 

async def renew_cancel_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    logger.info(f"User {update.effective_user.id} cancelled renewal.")

    await query.edit_message_text("Perpanjangan dibatalkan.")

    context.user_data.pop('renew_username', None)
    context.user_data.pop('selected_renew_type', None)
    context.user_data.pop('current_action', None)

    await query.message.reply_text("Silakan pilih menu lainnya:", reply_markup=keyboards.get_main_menu_keyboard())
    return ConversationHandler.END 

# --- SSH Creation Handlers ---
async def ssh_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text("Password:")
    return SSH_GET_PASSWORD

async def ssh_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['password'] = update.message.text
    await update.message.reply_text("Duration (days):")
    return SSH_GET_DURATION

async def ssh_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        duration = int(update.message.text)
        context.user_data['duration'] = duration
        await update.message.reply_text("IP Limit:")
        return SSH_GET_IP_LIMIT
    except ValueError:
        await update.message.reply_text("Duration must be a number. Please enter a valid duration.")
        return SSH_GET_DURATION

async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        ip_limit = int(update.message.text)
        context.user_data['ip_limit'] = ip_limit
        await update.message.reply_text("⏳ Creating SSH account...")

        ud = context.user_data
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_ssh.sh', ud['username'], ud['password'], str(ud['duration']), str(ud['ip_limit'])],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text( 
            f"✅ Result:\n{p.stdout}",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update, context, e)

    context.user_data.clear()
    return ROUTE

# --- VMESS Handlers ---
async def vmess_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text
    await update.message.reply_text("Duration (days):")
    return VMESS_GET_DURATION

async def vmess_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    ud = context.user_data
    await update.message.reply_text("⏳ Creating VMESS account...")

    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_vmess_user.sh', ud['user'], ud['duration']],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text( 
            f"✅ Result:\n{p.stdout}",
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update, context, e)

    context.user_data.clear()
    return ROUTE

# --- VLESS Handlers ---
async def vless_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text
    await update.message.reply_text("Masukkan durasi akun VLESS (hari):")
    return VLESS_GET_DURATION

async def vless_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    ud = context.user_data
    await update.message.reply_text("Masukkan batas IP untuk akun VLESS:") # Minta IP Limit
    return VLESS_GET_IP_LIMIT # Transisi ke state IP Limit

async def vless_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        ip_limit = int(update.message.text)
        context.user_data['ip_limit'] = ip_limit
        await update.message.reply_text("Masukkan kuota GB untuk akun VLESS:") # Minta Kuota GB
        return VLESS_GET_QUOTA # Transisi ke state Kuota GB
    except ValueError:
        await update.message.reply_text("Batas IP harus berupa angka. Silakan masukkan batas IP yang valid.")
        return VLESS_GET_IP_LIMIT # Tetap di state ini

async def vless_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        quota_gb = int(update.message.text)
        context.user_data['quota_gb'] = quota_gb
        await update.message.reply_text("⏳ Creating VLESS account...")

        ud = context.user_data
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_vless_user.sh', ud['user'], str(ud['duration']), str(ud['ip_limit']), str(ud['quota_gb'])], 
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text( 
            f"✅ Result:\n{p.stdout}", # Plain text
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- TROJAN Handlers ---
async def trojan_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text
    await update.message.reply_text("Masukkan durasi akun TROJAN (hari):")
    return TROJAN_GET_DURATION

async def trojan_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text
    ud = context.user_data
    await update.message.reply_text("Masukkan batas IP untuk akun TROJAN:") # Minta IP Limit
    return TROJAN_GET_IP_LIMIT 

async def trojan_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    try:
        ip_limit = int(update.message.text)
        context.user_data['ip_limit'] = ip_limit
        await update.message.reply_text("Masukkan kuota GB untuk akun TROJAN:") # Minta Kuota GB
        return TROJAN_GET_QUOTA 
    except ValueError:
        await update.message.reply_text("Batas IP harus berupa angka. Silakan masukkan batas IP yang valid.")
        return TROJAN_GET_IP_LIMIT 

async def trojan_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int: 
    try:
        quota_gb = int(update.message.text)
        context.user_data['quota_gb'] = quota_gb
        await update.message.reply_text("⏳ Creating TROJAN account...")

        ud = context.user_data
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_trojan_user.sh', ud['user'], str(ud['duration']), str(ud['ip_limit']), str(ud['quota_gb'])], 
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text( 
            f"✅ Result:\n{p.stdout}", # Plain text
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update, context, e)
    context.user_data.clear()
    return ROUTE

# --- Conversation Control ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        context.user_data.clear()
    await update.message.reply_text("Operation cancelled.")
    return ConversationHandler.END

async def back_to_menu_from_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data:
        context.user_data.clear()
    await update.message.reply_text("Cancelled, returning to main menu.")
    return await menu(update, context)
