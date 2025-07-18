# File: handlers.py (Versi Final dengan Fitur Trial Vmess)

import subprocess, re, logging
from telegram import Update
from telegram.ext import (
    ContextTypes, ConversationHandler,
    MessageHandler, filters, CallbackQueryHandler, CommandHandler
)
import keyboards, config, database

(ROUTE, SSH_GET_USERNAME, SSH_GET_PASSWORD, SSH_GET_DURATION, SSH_GET_IP_LIMIT, VMESS_GET_USER, VMESS_GET_DURATION, VMESS_GET_IP_LIMIT, VMESS_GET_QUOTA, VLESS_GET_USER, VLESS_GET_DURATION, VLESS_GET_IP_LIMIT, VLESS_GET_QUOTA, TROJAN_GET_USER, TROJAN_GET_DURATION, TROJAN_GET_IP_LIMIT, TROJAN_GET_QUOTA) = range(17)

def is_admin(update: Update) -> bool: return update.effective_user.id == config.ADMIN_TELEGRAM_ID
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user; database.add_user_if_not_exists(user.id, user.first_name, user.username)
    user_info = (f"<b>Informasi Profil Anda:</b>\n-----------------------------------\n<b>ID Pengguna:</b> <code>{user.id}</code>\n<b>Nama Depan:</b> {user.first_name}\n<b>Nama Belakang:</b> {user.last_name or 'Tidak ada'}\n<b>Username:</b> @{user.username or 'Tidak ada'}\n<b>Kode Bahasa:</b> {user.language_code or 'Tidak diketahui'}\n-----------------------------------\n\nGunakan /menu untuk melihat semua fitur.")
    try:
        photos = await user.get_profile_photos(limit=1)
        if photos and photos.photos: await update.message.reply_photo(photo=photos.photos[0][-1].file_id, caption=user_info, parse_mode='HTML')
        else: await update.message.reply_text(user_info, parse_mode='HTML')
    except Exception: await update.message.reply_text(user_info, parse_mode='HTML')
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Pilih menu:", reply_markup=keyboards.get_main_menu_keyboard()); return ROUTE
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not is_admin(update): await update.message.reply_text("Perintah ini hanya untuk Admin."); return
    await update.message.reply_text("Selamat datang di Panel Admin.")

async def route_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query; await query.answer(); command = query.data
    if command == "back_to_main_menu": await query.edit_message_text("Kembali ke menu utama.", reply_markup=keyboards.get_main_menu_keyboard()); return ROUTE
    if command == "menu_ssh": await query.edit_message_text("<b>SSH PANEL MENU</b>", reply_markup=keyboards.get_ssh_menu_keyboard(), parse_mode='HTML'); return ROUTE
    if command == "ssh_add": await query.edit_message_text("Masukkan <b>Username</b> untuk akun SSH:", parse_mode='HTML'); return SSH_GET_USERNAME
    if command == "ssh_trial":
        await query.edit_message_text("⏳ Memproses pembuatan akun trial SSH...")
        try:
            p = subprocess.run(['sudo', '/opt/hokage-bot/create_trial_ssh.sh'], capture_output=True, text=True, check=True, timeout=30)
            await query.edit_message_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
        except Exception as e: return await handle_script_error(query, context, e)
        return ROUTE
    if command == "menu_vmess":
        await query.edit_message_text("<b>VMESS PANEL MENU</b>", reply_markup=keyboards.get_vmess_menu_keyboard(), parse_mode='HTML')
        return ROUTE
    if command == "vmess_add":
        await query.edit_message_text("Masukkan <b>User</b> untuk akun Vmess:", parse_mode='HTML'); return VMESS_GET_USER
    if command == "vmess_trial":
        await query.edit_message_text("⏳ Memproses pembuatan akun trial Vmess...")
        try:
            p = subprocess.run(['sudo', '/opt/hokage-bot/create_trial_vmess.sh'], capture_output=True, text=True, check=True, timeout=30)
            await query.edit_message_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
        except Exception as e: return await handle_script_error(query, context, e)
        return ROUTE
    if command == "menu_vless": await query.edit_message_text("Masukkan <b>User</b> untuk akun Vless:", parse_mode='HTML'); return VLESS_GET_USER
    if command == "menu_trojan": await query.edit_message_text("Masukkan <b>User</b> untuk akun Trojan:", parse_mode='HTML'); return TROJAN_GET_USER
    if command == "close_menu": await query.edit_message_text("Menu ditutup. Kirim /menu untuk membuka lagi."); return ConversationHandler.END
    else: await query.edit_message_text(f"Fitur <b>{command}</b> belum siap.", parse_mode='HTML'); return ROUTE

async def handle_script_error(query, context: ContextTypes.DEFAULT_TYPE, error: Exception):
    update_obj = query.message if query else context
    if isinstance(error, subprocess.CalledProcessError):
        error_message = error.stdout.strip() or error.stderr.strip()
        await update_obj.reply_text(f"❌ <b>Gagal:</b>\n<pre>{error_message}</pre>", parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    else:
        await update_obj.reply_text(f"❌ Error: {error}", reply_markup=keyboards.get_back_to_menu_keyboard())
    context.user_data.clear(); return ROUTE
async def ssh_get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_username'] = update.message.text; await update.message.reply_text("<b>Password</b>:", parse_mode='HTML'); return SSH_GET_PASSWORD
async def ssh_get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_password'] = update.message.text; await update.message.reply_text("<b>Masa Aktif</b> (hari):", parse_mode='HTML'); return SSH_GET_DURATION
async def ssh_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_duration'] = update.message.text; await update.message.reply_text("<b>Limit IP</b>:", parse_mode='HTML'); return SSH_GET_IP_LIMIT
async def ssh_get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['ssh_ip_limit'] = update.message.text; await update.message.reply_text("⏳ Memproses SSH...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_ssh_user.sh', context.user_data['ssh_username'], context.user_data['ssh_password'], context.user_data['ssh_duration'], context.user_data['ssh_ip_limit']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: return await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END
async def vmess_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_user'] = update.message.text; await update.message.reply_text("<b>Masa Aktif</b> (hari):", parse_mode='HTML'); return VMESS_GET_DURATION
async def vmess_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_duration'] = update.message.text; await update.message.reply_text("<b>Limit IP</b> (0=unlimited):", parse_mode='HTML'); return VMESS_GET_IP_LIMIT
async def vmess_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_ip_limit'] = update.message.text; await update.message.reply_text("<b>Kuota</b> (GB, 0=unlimited):", parse_mode='HTML'); return VMESS_GET_QUOTA
async def vmess_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vmess_quota'] = update.message.text; await update.message.reply_text("⏳ Memproses Vmess...")
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vmess_user.sh', context.user_data['vmess_user'], context.user_data['vmess_duration'], context.user_data['vmess_ip_limit'], context.user_data['vmess_quota']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: return await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END
async def vless_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_user'] = update.message.text; await update.message.reply_text("<b>Masa Aktif</b> (hari):", parse_mode='HTML'); return VLESS_GET_DURATION
async def vless_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_duration'] = update.message.text; await update.message.reply_text("<b>Limit IP</b> (0=unlimited):", parse_mode='HTML'); return VLESS_GET_IP_LIMIT
async def vless_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_ip_limit'] = update.message.text; await update.message.reply_text("<b>Kuota</b> (GB, 0=unlimited):", parse_mode='HTML'); return VLESS_GET_QUOTA
async def vless_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vless_quota'] = update.message.text; await update.message.reply_text("⏳ Memproses Vless...");
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_vless_user.sh', context.user_data['vless_user'], context.user_data['vless_duration'], context.user_data['vless_ip_limit'], context.user_data['vless_quota']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: return await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END
async def trojan_get_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['trojan_user'] = update.message.text; await update.message.reply_text("<b>Masa Aktif</b> (hari):", parse_mode='HTML'); return TROJAN_GET_DURATION
async def trojan_get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['trojan_duration'] = update.message.text; await update.message.reply_text("<b>Limit IP</b> (0=unlimited):", parse_mode='HTML'); return TROJAN_GET_IP_LIMIT
async def trojan_get_ip_limit(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['trojan_ip_limit'] = update.message.text; await update.message.reply_text("<b>Kuota</b> (GB, 0=unlimited):", parse_mode='HTML'); return TROJAN_GET_QUOTA
async def trojan_get_quota_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['trojan_quota'] = update.message.text; await update.message.reply_text("⏳ Memproses Trojan...");
    try:
        p = subprocess.run(['sudo', '/opt/hokage-bot/create_trojan_user.sh', context.user_data['trojan_user'], context.user_data['trojan_duration'], context.user_data['trojan_ip_limit'], context.user_data['trojan_quota']], capture_output=True, text=True, check=True, timeout=30)
        await update.message.reply_text(p.stdout, parse_mode='HTML', reply_markup=keyboards.get_back_to_menu_keyboard())
    except Exception as e: return await handle_script_error(update.message, context, e)
    context.user_data.clear(); return ConversationHandler.END
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if context.user_data: context.user_data.clear()
    await update.message.reply_text("Dibatalkan."); return ConversationHandler.END
