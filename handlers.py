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
import keyboards, config, database

# Define all Conversation states
(
    ROUTE,
    SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT,
    VMESS_GET_USER, VMESS_GET_DURATION,
    VLESS_GET_USER, VLESS_GET_DURATION,
    TROJAN_GET_USER, TROJAN_GET_DURATION,
    SSH_RENEW_USER, SSH_RENEW_DAYS
) = range(13)

# --- Helper Functions ---
def is_admin(update: Update) -> bool:
    return update.effective_user.id == config.ADMIN_TELEGRAM_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    database.add_user_if_not_exists(user.id, user.first_name, user.username)
    await update.message.reply_text(
        "🤖 Welcome to SSH/VPN Management Bot!\n\n"
        "Use /menu to access all features.",
        reply_markup=keyboards.get_main_menu_keyboard()
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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

# --- Main Handler ---
async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    command = query.data

    # Navigation handlers
    if command in ["main_menu", "back_to_main_menu"]:
        await query.edit_message_text(
            "Main Menu:",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        return ROUTE

    # Menu selection
    menu_map = {
        "menu_ssh": "SSH",
        "menu_vmess": "VMESS",
        "menu_vless": "VLESS",
        "menu_trojan": "TROJAN"
    }
    if command in menu_map:
        keyboard_func = getattr(keyboards, f"get_{menu_map[command].lower()}_menu_keyboard")
        await query.edit_message_text(
            f"<b>{menu_map[command]} PANEL MENU</b>",
            reply_markup=keyboard_func(),
            parse_mode='HTML'
        )
        return ROUTE

    # Special actions
    if command == "menu_restore":
        text = ("⚠️ <b>WARNING!</b> ⚠️\n\nYou are about to perform a <b>RESTORE</b> from latest backup. "
                "This will <b>OVERWRITE ALL CONFIGURATIONS</b>. Are you sure?")
        restore_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Yes, Proceed", callback_data="confirm_restore")],
            [InlineKeyboardButton("❌ Cancel", callback_data="main_menu")]
        ])
        await query.edit_message_text(text, parse_mode='HTML', reply_markup=restore_keyboard)
        return ROUTE

    # Script execution commands
    script_map = {
        "ssh_trial": "create_trial_ssh.sh",
        "vmess_trial": "create_trial_vmess.sh",
        "vless_trial": "create_trial_vless.sh",
        "trojan_trial": "create_trial_trojan.sh",
        "menu_restart": "restart_for_bot.sh",
        "menu_running": "check_status_for_bot.sh",
        "menu_backup": "backup_for_bot.sh",
        "confirm_restore": "restore_for_bot.sh",
        "ssh_renew": "create_renew_ssh.sh"
    }

    if command in script_map:
        if command == "ssh_renew":
            await query.edit_message_text(
                "<b>Enter SSH username to renew:</b>",
                parse_mode='HTML'
            )
            return SSH_RENEW_USER

        wait_message = f"⏳ Processing {command.replace('_', ' ').title()}..."
        timeout = 120
        if command in ["confirm_restore", "menu_backup"]:
            wait_message = f"⚙️ *Starting {command.replace('menu_', '')} process...*\n\nThis may take several minutes."
            timeout = 300

        await query.edit_message_text(wait_message, parse_mode='Markdown')
        try:
            p = subprocess.run(
                ['sudo', f'/opt/hokage-bot/{script_map[command]}'],
                capture_output=True,
                text=True,
                check=True,
                timeout=timeout
            )
            await query.edit_message_text(
                f"✅ Result:\n<pre>{p.stdout}</pre>",
                parse_mode='HTML',
                reply_markup=keyboards.get_back_to_menu_keyboard()
            )
        except Exception as e:
            return await handle_script_error(query, context, e)
        return ROUTE

    # Conversation starters
    conv_starters = {
        "ssh_add": ("SSH Username:", SSH_GET_USERNAME),
        "vmess_add": ("VMESS Username:", VMESS_GET_USER),
        "vless_add": ("VLESS Username:", VLESS_GET_USER),
        "trojan_add": ("Trojan Username:", TROJAN_GET_USER)
    }
    if command in conv_starters:
        text, state = conv_starters[command]
        await query.edit_message_text(f"<b>{text}</b>", parse_mode='HTML')
        return state

    if command == "close_menu":
        await query.edit_message_text("Menu closed.")
        return ConversationHandler.END

    await query.edit_message_text(
        f"Feature <b>{command}</b> is not ready yet.",
        parse_mode='HTML',
        reply_markup=keyboards.get_back_to_menu_keyboard()
    )
    return ROUTE

# --- SSH Renewal Handlers ---
async def ssh_renew_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_renew_user'] = update.message.text
    await update.message.reply_text(
        "<b>Enter number of days to extend:</b>",
        parse_mode='HTML'
    )
    return SSH_RENEW_DAYS

async def ssh_renew_days(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_renew_days'] = update.message.text
    user = context.user_data['ssh_renew_user']
    days = context.user_data['ssh_renew_days']
    admin_id = update.effective_user.id

    await update.message.reply_text("⏳ Processing SSH account renewal...")

    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_renew_ssh.sh', user, days, str(admin_id)],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text(
            p.stdout,
            parse_mode='HTML',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update.message, context, e)

    context.user_data.clear()
    return ROUTE

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
    context.user_data['duration'] = update.message.text
    await update.message.reply_text("IP Limit:")
    return SSH_GET_IP_LIMIT

async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ip_limit'] = update.message.text
    await update.message.reply_text("⏳ Creating SSH account...")
    
    ud = context.user_data
    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_ssh.sh', ud['username'], ud['password'], ud['duration'], ud['ip_limit']],
            capture_output=True,
            text=True,
            check=True,
            timeout=30
        )
        await update.message.reply_text(
            p.stdout,
            parse_mode='HTML',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update.message, context, e)
    
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
            p.stdout,
            parse_mode='HTML',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    except Exception as e:
        await handle_script_error(update.message, context, e)
    
    context.user_data.clear()
    return ROUTE

# --- Error Handler ---
async def handle_script_error(update_obj, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    msg = f"Error occurred: {error}"
    if isinstance(error, subprocess.CalledProcessError):
        msg = error.stdout.strip() or error.stderr.strip() or "Script failed without error output."
    
    if hasattr(update_obj, 'edit_message_text'):
        await update_obj.edit_message_text(
            f"❌ <b>Failed:</b>\n<pre>{msg}</pre>",
            parse_mode='HTML',
            reply_markup=keyboards.get_back_to_menu_keyboard()
        )
    else:
        await update_obj.reply_text(
            f"❌ <b>Failed:</b>\n<pre>{msg}</pre>",
            parse_mode='HTML',
            reply_markup=keyboards.get_main_menu_keyboard()
        )
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
