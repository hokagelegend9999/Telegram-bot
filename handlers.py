# File: handlers.py
# Versi final dengan sintaks yang sudah diperbaiki.

import subprocess, re, logging
from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, filters, CallbackQueryHandler, CommandHandler
)
import keyboards, config, database

# Definisikan State untuk SEMUA Conversation
(
    SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT,
    VMESS_GET_USER, VMESS_GET_DURATION, VMESS_GET_IP_LIMIT, VMESS_GET_QUOTA,
    VLESS_GET_USER, VLESS_GET_DURATION, VLESS_GET_IP_LIMIT, VLESS_GET_QUOTA
) = range(12)

def is_admin(update: Update) -> bool:
    return update.effective_user.id == config.ADMIN_TELEGRAM_ID

# --- HANDLER PERINTAH ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    database.add_user_if_not_exists(user.id, user.first_name, user.username)
    user_info = f"<b>ID:</b> <code>{user.id}</code>\n<b>Nama:</b> {user.first_name}\n\nSelamat datang! Gunakan /menu."
    await update.message.reply_text(user_info, parse_mode='HTML')

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Pilih menu:", reply_markup=keyboards.get_main_menu_keyboard())

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update):
        await update.message.reply_text("Perintah ini hanya untuk Admin.")
        return
    await update.message.reply_text("Selamat datang di Panel Admin.")

# --- HANDLER TOMBOL & NAVIGASI ---
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    command = query.data

    if command == "back_to_main_menu":
        await query.edit_message_text("Kembali ke menu utama.", reply_markup=keyboards.get_main_menu_keyboard())
        return ConversationHandler.END
    if command == "menu_ssh":
        await query.edit_message_text("<b>SSH PANEL MENU</b>", reply_markup=keyboards.get_ssh_menu_keyboard(), parse_mode='HTML')
        return ConversationHandler.END
    if command == "ssh_add":
        await query.edit_message_text("Masukkan <b>Username</b> untuk akun SSH:", parse_mode='HTML')
        return SSH_GET_USERNAME
    if command == "menu_vmess":
        await query.edit_message_text("Masukkan <b>User</b> untuk akun Vmess:", parse_mode='HTML')
        return VMESS_GET_USER
    if command == "menu_vless":
        await query.edit_message_text("Masukkan <b>User</b> untuk akun Vless:", parse_mode='HTML')
        return VLESS_GET_USER
    else:
        await query.edit_message_text(f"Fitur <b>{command}</b> belum siap.", parse_mode='HTML')
        return ConversationHandler.END

# --- CONVERSATION HANDLER UNTUK SSH ---
async def ssh_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_username'] = update.message.text
    await update.message.reply_text("Masukkan <b>Password</b>:", parse_mode='HTML')
    return SSH_GET_PASSWORD

async def ssh_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_password'] = update.message.text
    await update.message.reply_text("Masukkan <b>Masa Aktif</b> (hari):", parse_mode='HTML')
    return SSH_GET_DURATION

async def ssh_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_duration'] = update.message.text
    await update.message.reply_text("Masukkan <b>Limit IP</b>:", parse_mode='HTML')
    return SSH_GET_IP_LIMIT

async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_ip_limit'] = update.message.text
    await update.message.reply_text("⏳ Memproses pembuatan akun SSH...")
    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_ssh_user.sh', context.user_data['ssh_username'], context.user_data['ssh_password'], context.user_data['ssh_duration'], context.user_data['ssh_ip_limit']],
            capture_output=True, text=True, check=True, timeout=30
        )
        await update.message.reply_text(p.stdout, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal: {e}")
    context.user_data.clear()
    return ConversationHandler.END

# --- CONVERSATION HANDLER UNTUK VMESS ---
async def vmess_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_user'] = update.message.text
    await update.message.reply_text("Masukkan <b>Masa Aktif</b> (hari):", parse_mode='HTML')
    return VMESS_GET_DURATION

async def vmess_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_duration'] = update.message.text
    await update.message.reply_text("Masukkan <b>Limit IP</b> (0=unlimited):", parse_mode='HTML')
    return VMESS_GET_IP_LIMIT

async def vmess_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_ip_limit'] = update.message.text
    await update.message.reply_text("Masukkan <b>Kuota</b> (GB, 0=unlimited):", parse_mode='HTML')
    return VMESS_GET_QUOTA

async def vmess_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_quota'] = update.message.text
    await update.message.reply_text("⏳ Memproses pembuatan akun Vmess...")
    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_vmess_user.sh', context.user_data['vmess_user'], context.user_data['vmess_duration'], context.user_data['vmess_ip_limit'], context.user_data['vmess_quota']],
            capture_output=True, text=True, check=True, timeout=30
        )
        await update.message.reply_text(p.stdout, parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"❌ Gagal: {e}")
    context.user_data.clear()
    return ConversationHandler.END

# --- CONVERSATION HANDLER UNTUK VLESS ---
async def vless_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_user'] = update.message.text
    await update.message.reply_text("Masukkan <b>Masa Aktif</b> (hari):", parse_mode='HTML')
    return VLESS_GET_DURATION

async def vless_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_duration'] = update.message.text
    await update.message.reply_text("Masukkan <b>Limit IP</b> (0 untuk unlimited):", parse_mode='HTML')
    return VLESS_GET_IP_LIMIT

async def vless_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_ip_limit'] = update.message.text
    await update.message.reply_text("Masukkan <b>Kuota</b> (GB, 0 untuk unlimited):", parse_mode='HTML')
    return VLESS_GET_QUOTA

async def vless_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_quota'] = update.message.text
    await update.message.reply_text("⏳ Memproses pembuatan akun Vless...")
    try:
        p = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_vless_user.sh', context.user_data['vless_user'], context.user_data['vless_duration'], context.user_data['vless_ip_limit'], context.user_data['vless_quota']],
            capture_output=True, text=True, check=True, timeout=30
        )
        await update.message.reply_text(p.stdout, parse_mode='HTML')
    except subprocess.CalledProcessError as e:
        await update.message.reply_text(f"❌ Gagal:\n<pre>{e.stdout or e.stderr}</pre>", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"❌ Terjadi kesalahan fatal: {e}")
    context.user_data.clear()
    return ConversationHandler.END

# --- FUNGSI PEMBATALAN ---
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Proses dibatalkan.")
    context.user_data.clear()
    return ConversationHandler.END
