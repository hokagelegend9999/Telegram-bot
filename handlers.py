# File: handlers.py (Versi Final Absolut)

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

# Definisikan semua State untuk alur Conversation
(
    ROUTE,
    SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT,
    VMESS_GET_USER, VMESS_GET_DURATION,
    VLESS_GET_USER, VLESS_GET_DURATION,
    TROJAN_GET_USER, TROJAN_GET_DURATION
) = range(11)

# --- Fungsi Bantuan & Perintah Dasar ---
def is_admin(update: Update) -> bool: return update.effective_user.id == config.ADMIN_TELEGRAM_ID
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user; database.add_user_if_not_exists(user.id, user.first_name, user.username)
    await update.message.reply_text("Selamat datang! Gunakan /menu untuk melihat semua fitur.")
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Silakan pilih dari menu di bawah:", reply_markup=keyboards.get_main_menu_keyboard()); return ROUTE
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update): await update.message.reply_text("Perintah ini hanya untuk Admin."); return
    await update.message.reply_text("Selamat datang di Panel Admin.")

# --- Handler Tombol & Router Utama ---
async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query; await query.answer(); command = query.data
    if command in ["main_menu", "back_to_main_menu"]:
        await query.edit_message_text("Menu Utama:", reply_markup=keyboards.get_main_menu_keyboard()); return ROUTE
    menu_map = {"menu_ssh": "SSH", "menu_vmess": "VMESS", "menu_vless": "VLESS", "menu_trojan": "TROJAN"}
    if command in menu_map:
        keyboard_func = getattr(keyboards, f"get_{menu_map[command].lower()}_menu_keyboard")
        await query.edit_message_text(f"<b>{menu_map[command]} PANEL MENU</b>", reply_markup=keyboard_func(), parse_mode='HTML'); return ROUTE
    if command == "menu_restore":
        text = ("⚠️ <b>PERINGATAN!</b> ⚠️\n\nAnda akan menjalankan proses <b>RESTORE</b> dari backup terbaru. "
                "Tindakan ini akan <b>MENIMPA SEMUA KONFIGURASI</b>. Yakin ingin melanjutkan?")
        restore_keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("✅ Ya, Lanjutkan Restore", callback_data="confirm_restore")],
            [InlineKeyboardButton("❌ Batal", callback_data="main_menu")]
        ]); await query.edit_message_text(text, parse_mode='HTML', reply_markup=restore_keyboard); return ROUTE
    script_map = { "ssh_trial": "create_trial_ssh.sh", "vmess_trial": "create_trial_vmess.sh", "vless_trial": "create_trial_vless.sh", "trojan_trial": "create_trial_trojan.sh", "menu_restart": "restart_for_bot.sh", "menu_running": "check_status_for_bot.sh", "menu_backup": "backup_for_bot.sh", "confirm_restore": "restore_for_bot.sh" }
    if command in script_map:
        wait_message = f"⏳ Memproses {command.replace('_', ' ').replace('menu ', '').title()}..."; timeout = 120
        if command in ["confirm_restore", "menu_backup"]:
            wait_message = f"⚙️ *Memulai proses {command.replace('menu_', '')}...*\n\nIni bisa memakan waktu beberapa menit."; timeout = 300
        await query.edit_message_text(wait_message, parse_mode='Markdown')
        try:
            p = subprocess.run(['sudo', f'/opt/hokage-bot/{script_map[command]}'], capture_output=True, text=True, check=True, timeout=timeout)
            await query.edit_message_text(f"✅ Hasil:\n<pre>{p.stdout}</pre>", parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
        except Exception as e: return await handle_script_error(query, context, e)
        return ROUTE
    conv_starters = { "ssh_add": ("Username SSH:", SSH_GET_USERNAME), "vmess_add": ("User Vmess:", VMESS_GET_USER), "vless_add": ("User Vless:", VLESS_GET_USER), "trojan_add": ("User Trojan:", TROJAN_GET_USER) }
    if command in conv_starters: text, state = conv_starters[command]; await query.edit_message_text(f"<b>{text}</b>", parse_mode='HTML'); return state
    if command == "close_menu": await query.edit_message_text("Menu ditutup."); return ConversationHandler.END
    await query.edit_message_text(f"Fitur <b>{command}</b> belum siap.", parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard()); return ROUTE

async def handle_script_error(update_obj, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    msg = f"Error: {error}"
    if isinstance(error, subprocess.CalledProcessError): msg = error.stdout.strip() or error.stderr.strip() or "Skrip gagal tanpa output error."
    if hasattr(update_obj, 'edit_message_text'):
        await update_obj.edit_message_text(f"❌ <b>Gagal:</b>\n<pre>{msg}</pre>", parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    else:
        await update_obj.reply_text(f"❌ <b>Gagal:</b>\n<pre>{msg}</pre>", parse_mode='HTML', reply_markup=keyboards.get_main_menu_keyboard())
    return ROUTE

# --- [FUNGSI CONVERSATION DENGAN LOGIKA PENUH] ---
async def ssh_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text; await update.message.reply_text("Password:"); return SSH_GET_PASSWORD
async def ssh_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['password'] = update.message.text; await update.message.reply_text("Masa Aktif (hari):"); return SSH_GET_DURATION
async def ssh_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text; await update.message.reply_text("Limit IP:"); return SSH_GET_IP_LIMIT
async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ip_limit'] = update.message.text; await update.message.reply_text("⏳ Memproses Akun SSH...")
    ud = context.user_data
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_ssh.sh', ud['username'], ud['password'], ud['duration'], ud['ip_limit']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END

async def vmess_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text; await update.message.reply_text("Masa Aktif (hari):"); return VMESS_GET_DURATION
async def vmess_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text; ud = context.user_data; await update.message.reply_text("⏳ Memproses Akun Vmess...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vmess_user.sh', ud['user'], ud['duration']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END

async def vless_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text; await update.message.reply_text("Masa Aktif (hari):"); return VLESS_GET_DURATION
async def vless_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text; ud = context.user_data; await update.message.reply_text("⏳ Memproses Akun Vless...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vless_user.sh', ud['user'], ud['duration']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END

async def trojan_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['user'] = update.message.text; await update.message.reply_text("Masa Aktif (hari):"); return TROJAN_GET_DURATION
async def trojan_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['duration'] = update.message.text; ud = context.user_data; await update.message.reply_text("⏳ Memproses Akun Trojan...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trojan_user.sh', ud['user'], ud['duration']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END

# --- Fallback & Cancel ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data: context.user_data.clear()
    await update.message.reply_text("Proses dibatalkan."); return ConversationHandler.END

async def back_to_menu_from_conv(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data: context.user_data.clear()
    await update.message.reply_text("Dibatalkan, kembali ke menu utama."); return await menu(update, context)
