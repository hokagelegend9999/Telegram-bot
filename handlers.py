# handlers.py

import logging, json, subprocess, re
from telegram import Update
from telegram.ext import (
    ContextTypes, 
    ConversationHandler, 
    CommandHandler, 
    MessageHandler,
    CallbackQueryHandler,
    filters
)

import database, keyboards, config

# State untuk conversation
USER_USERNAME, USER_DURATION, USER_PASSWORD = range(3)
ADMIN_USERNAME, ADMIN_DURATION, ADMIN_PASSWORD = range(3, 6)

def is_admin(telegram_id: int) -> bool:
    user_data = database.get_user(telegram_id)
    return user_data and user_data['role'] == 'admin'

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani perintah /start dan tombol kembali ke menu."""
    user = update.effective_user
    database.add_user_if_not_exists(user.id, user.first_name, user.username)

    # PERBAIKAN: Set peran ke admin terlebih dahulu jika dia adalah admin utama
    if user.id == config.ADMIN_TELEGRAM_ID:
        database.update_role(user.id, 'admin')

    # Setelah peran dipastikan benar, baru kirim menu yang sesuai
    if is_admin(user.id):
        await update.message.reply_text("Selamat datang kembali, Admin!", reply_markup=keyboards.ADMIN_MAIN_MENU)
    else:
        await update.message.reply_text(f"Selamat datang, {user.first_name}!", reply_markup=keyboards.get_user_main_menu(user.id))

async def switch_role(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != config.ADMIN_TELEGRAM_ID:
        await update.message.reply_text("Hanya Admin Utama yang dapat menggunakan fitur ini.")
        return

    # Set peran ke 'user' saat beralih
    database.update_role(user_id, 'user')
    await update.message.reply_text("✅ Anda sekarang dalam mode **User**.", parse_mode='Markdown', reply_markup=keyboards.get_user_main_menu(user_id))

async def message_router(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text
    user_id = update.effective_user.id

    if text == "💰 Cek Saldo": await cek_saldo(update, context)
    elif text == "➕ Top Up Saldo": await request_topup(update, context)
    elif text == "🛒 Beli Layanan": await show_buy_menu(update, context)
    elif text == "🎁 Akun Trial Gratis": await request_trial_ssh(update, context)
    elif text == "👥 Manajemen User" and is_admin(user_id): await manage_users(update, context)
    elif text == "➕ Top Up Manual" and is_admin(user_id): await topup_manual_prompt(update, context)
    elif text == "👤 Switch ke Mode User" and is_admin(user_id): await switch_role(update, context)
    elif text == "👑 Kembali ke Menu Admin" and user_id == config.ADMIN_TELEGRAM_ID:
        await start(update, context) # Panggil fungsi start untuk kembali
    elif text == "➕ Buat Akun SSH" and is_admin(user_id):
        await context.bot.send_message(chat_id=user_id, text="Memulai pembuatan akun manual untuk Admin...")
        return await admin_create_ssh_start(update, context)

# ... (sisa semua fungsi lain di bawah ini tidak berubah, biarkan seperti yang sudah ada) ...
async def request_trial_ssh(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not database.can_claim_trial(user_id):
        await update.message.reply_text("❌ Anda sudah mengambil akun trial hari ini. Silakan coba lagi besok.")
        return
    await update.message.reply_text("⏳ Sedang membuat akun trial Anda (aktif 60 menit), mohon tunggu...")
    trial_username = f"trial-{str(user_id)[-5:]}"
    try:
        process = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_trial_ssh.sh', trial_username],
            capture_output=True, text=True
        )
        details = json.loads(process.stdout)
        if details.get("status") == "success":
            database.update_last_trial_time(user_id)
            account_info = (
                f"✅  **Akun Trial SSH (60 Menit) Berhasil Dibuat** ✅\n\n"
                f"`--------------------------------------`\n"
                f" `Username`     : `{details['username']}`\n"
                f" `Password`     : `{details['password']}`\n"
                f" `Expires On`   : `{details['expires_on']}`\n"
                f"`--------------------------------------`\n"
                f" `IP Address`   : `{details['ip_address']}`\n"
                f" `Host`         : `{details['host']}`\n"
                f"`--------------------------------------`\n\n"
                f"⚙️  **Ports & Services**\n"
                f" `OpenSSH`      : `{details['port_openssh']}`\n"
                f" `SSH WS`       : `{details['port_ssh_ws']}`\n"
                f" `SSH SSL WS`   : `{details['port_ssh_ssl_ws']}`\n"
                f" `SSL/TLS`      : `{details['port_stunnel']}`\n"
                f" `Squid Proxy`  : `{details['port_squid']}`\n"
                f" `UDPGW`        : `{details['port_udpgw']}`\n\n"
                f"📡 **SlowDNS Info**\n"
                f" `Nameserver`   : `{details['ns_domain']}`\n"
                f" `Public Key`   : `{details['ns_pubkey']}`\n\n"
                f"🌐 **OpenVPN Config**\n"
                f" `TCP` : {details['ovpn_tcp_link']}\n"
                f" `UDP` : {details['ovpn_udp_link']}\n\n"
                f"📋 **Payload WS**\n"
                f"```\n{details['payload_ws']}\n```\n\n"
                f"📋 **Payload WSS**\n"
                f"```\n{details['payload_wss']}\n```\n"
                f"`--------------------------------------`"
            )
            await update.message.reply_text(account_info, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Gagal membuat akun trial: {details.get('error')}")
    except Exception as e:
        logging.error(f"Error saat membuat akun trial: {e}")
        await update.message.reply_text("❌ Terjadi kesalahan fatal di server. Hubungi admin.")
async def show_buy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Silakan pilih layanan:", reply_markup=keyboards.buy_service_menu())
async def cek_saldo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data = database.get_user(update.effective_user.id)
    balance = user_data['balance'] if user_data else 0
    await update.message.reply_text(f"Saldo Anda saat ini adalah: Rp {balance:,}")
async def request_topup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Silakan pilih metode top up:", reply_markup=keyboards.topup_choice_menu())
async def topup_choice_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    choice = query.data
    if choice == "topup_manual":
        user = query.from_user
        await query.edit_message_text(f"Permintaan Top Up Manual Anda telah dikirim ke Admin.\n\nSilakan hubungi Admin dan sebutkan ID: `{user.id}`", parse_mode='Markdown')
        admin_notif = f"🔔 Permintaan Top Up Manual!\n\nDari: {user.first_name} (@{user.username})\nID: `{user.id}`"
        await context.bot.send_message(chat_id=config.ADMIN_TELEGRAM_ID, text=admin_notif, parse_mode='Markdown')
    elif choice == "topup_auto_soon":
        await query.edit_message_text("Fitur Top Up Otomatis akan segera hadir! Mohon ditunggu ya.")
async def manage_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    all_users = database.get_all_users()
    response_text = "Daftar Pengguna:\n\n"
    for user in all_users:
        response_text += f"👤 Nama: {user['first_name']} (@{user['username']})\n   ID: `{user['telegram_id']}`\n   Role: {user['role']}\n   Saldo: Rp {user['balance']:,}\n   Trial Terakhir: {user['last_trial_claimed_at'] or 'Belum'}\n--------------------\n"
    await update.message.reply_text(response_text, parse_mode='Markdown')
async def topup_manual_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Gunakan format:\n`/topup [user_id] [jumlah_saldo]`\n\nContoh: `/topup 123456789 50000`", parse_mode='Markdown')
async def topup_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id): return
    try:
        target_id, amount = int(context.args[0]), int(context.args[1])
        target_user = database.get_user(target_id)
        if not target_user:
            await update.message.reply_text("User tidak ditemukan.")
            return
        database.update_balance(target_id, amount)
        new_balance = database.get_user(target_id)['balance']
        await update.message.reply_text(f"✅ Saldo untuk {target_user['first_name']} berhasil ditambah Rp {amount:,}.\nSaldo baru: Rp {new_balance:,}")
        await context.bot.send_message(chat_id=target_id, text=f"🎉 Saldo Anda ditambah admin sebesar Rp {amount:,}!\nSaldo baru: Rp {new_balance:,}")
    except (IndexError, ValueError):
        await update.message.reply_text("Format salah. Gunakan: /topup [user_id] [jumlah]")
async def process_ssh_creation(update: Update, context: ContextTypes.DEFAULT_TYPE, is_admin_flow: bool):
    if is_admin_flow:
        username, duration, password = context.user_data['admin_ssh_username'], context.user_data['admin_ssh_duration'], context.user_data['admin_ssh_password']
    else:
        username, duration, password = context.user_data['user_ssh_username'], context.user_data['user_ssh_duration'], context.user_data['user_ssh_password']
    user_id = update.effective_user.id
    await update.message.reply_text("⏳ Sedang memproses pembuatan akun, mohon tunggu...")
    try:
        process = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_ssh.sh', username, str(duration), password],
            capture_output=True, text=True
        )
        details = json.loads(process.stdout)
        if details.get("status") == "success":
            if not is_admin_flow:
                database.update_balance(user_id, -config.SSH_PRICE)
            account_info = (
                f"✅  **Akun SSH Berhasil Dibuat** ✅\n\n"
                f"`--------------------------------------`\n"
                f"  **Username** : `{details['username']}`\n"
                f"  **Password** : `{details['password']}`\n"
                f"  **Host / IP** : `{details['host']}`\n"
                f"  **Expires on** : `{details['expires_on']}`\n"
                f"`--------------------------------------`\n\n"
                f"⚙️  **Ports & Services**\n"
                f" `OpenSSH`      : `{details['port_openssh']}`\n"
                f" `SSH WS`       : `{details['port_ssh_ws']}`\n"
                f" `SSH SSL WS`   : `{details['port_ssh_ssl_ws']}`\n"
                f" `SSL/TLS`      : `{details['port_stunnel']}`\n"
                f" `Squid Proxy`  : `{details['port_squid']}`\n"
                f" `UDPGW`        : `{details['port_udpgw']}`\n\n"
                f"📡 **SlowDNS Info**\n"
                f" `Nameserver`   : `{details['ns_domain']}`\n"
                f" `Public Key`   : `{details['ns_pubkey']}`\n\n"
                f"🌐 **OpenVPN Config**\n"
                f" `TCP` : {details['ovpn_tcp_link']}\n"
                f" `UDP` : {details['ovpn_udp_link']}\n\n"
                f"📋 **Payload WS**\n"
                f"```\n{details['payload_ws']}\n```\n\n"
                f"📋 **Payload WSS**\n"
                f"```\n{details['payload_wss']}\n```\n"
                f"`--------------------------------------`"
            )
            await update.message.reply_text(account_info, parse_mode='Markdown')
        else:
            await update.message.reply_text(f"❌ Gagal membuat akun: {details.get('error', 'Error tidak diketahui')}")
    except Exception as e:
        logging.error(f"Error saat membuat SSH: {e}")
        await update.message.reply_text(f"❌ Terjadi kesalahan fatal di server. Hubungi admin.")
    return ConversationHandler.END
async def cancel_conversation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Proses dibatalkan.")
    await start(update, context)
    return ConversationHandler.END
async def buy_ssh_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_data = database.get_user(user_id)
    if user_data['balance'] < config.SSH_PRICE:
        await query.edit_message_text(f"Maaf, saldo Anda tidak mencukupi (Rp {user_data['balance']:,}).")
        return ConversationHandler.END
    await query.edit_message_text("Silakan masukkan **Username** yang Anda inginkan:", parse_mode='Markdown')
    return USER_USERNAME
async def user_get_ssh_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text.lower()
    if not re.match("^[a-z0-9]{4,12}$", username):
        await update.message.reply_text("Username tidak valid.\nHarus 4-12 karakter, hanya huruf kecil dan angka.")
        return USER_USERNAME
    context.user_data['user_ssh_username'] = username
    await update.message.reply_text("Masukkan masa aktif akun (contoh: 30 untuk 30 hari):")
    return USER_DURATION
async def user_get_ssh_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        duration = int(update.message.text)
        if not 1 <= duration <= 365: raise ValueError()
        context.user_data['user_ssh_duration'] = duration
        await update.message.reply_text("Terakhir, masukkan **Password** yang Anda inginkan (minimal 4 karakter):", parse_mode='Markdown')
        return USER_PASSWORD
    except (ValueError):
        await update.message.reply_text("Masa aktif tidak valid. Masukkan angka antara 1 dan 365.")
        return USER_DURATION
async def user_get_ssh_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text
    if len(password) < 4:
        await update.message.reply_text("Password terlalu pendek. Masukkan minimal 4 karakter.")
        return USER_PASSWORD
    context.user_data['user_ssh_password'] = password
    return await process_ssh_creation(update, context, is_admin_flow=False)
async def admin_create_ssh_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("**(Admin)** Masukkan **Username** untuk akun baru:", parse_mode='Markdown')
    return ADMIN_USERNAME
async def admin_get_ssh_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text.lower()
    if not re.match("^[a-z0-9]{4,12}$", username):
        await update.message.reply_text("Username tidak valid.\nHarus 4-12 karakter, hanya huruf kecil dan angka.")
        return ADMIN_USERNAME
    context.user_data['admin_ssh_username'] = username
    await update.message.reply_text("**(Admin)** Masukkan masa aktif akun (contoh: 30 hari):")
    return ADMIN_DURATION
async def admin_get_ssh_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        duration = int(update.message.text)
        if not 1 <= duration <= 365: raise ValueError()
        context.user_data['admin_ssh_duration'] = duration
        await update.message.reply_text("**(Admin)** Masukkan **Password** untuk akun ini:", parse_mode='Markdown')
        return ADMIN_PASSWORD
    except (ValueError):
        await update.message.reply_text("Masa aktif tidak valid. Masukkan angka antara 1 dan 365.")
        return ADMIN_DURATION
async def admin_get_ssh_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text
    if len(password) < 4:
        await update.message.reply_text("Password terlalu pendek. Masukkan minimal 4 karakter.")
        return ADMIN_PASSWORD
    context.user_data['admin_ssh_password'] = password
    return await process_ssh_creation(update, context, is_admin_flow=True)
