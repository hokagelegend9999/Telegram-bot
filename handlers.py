# File: handlers.py
# Versi baru dengan ConversationHandler untuk membuat akun SSH.

import subprocess
import re
from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters
)

# Impor dari file lokal Anda
import keyboards
import config
import database

# Definisikan State untuk Conversation
(
    GET_USERNAME,
    GET_PASSWORD,
    GET_DURATION,
    GET_IP_LIMIT
) = range(4)


# --- FUNGSI BANTUAN ---
def is_admin(update: Update) -> bool:
    """Memeriksa apakah pengguna adalah admin utama."""
    return update.effective_user.id == config.ADMIN_TELEGRAM_ID


# --- HANDLER UNTUK PERINTAH ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fungsi untuk perintah /start."""
    user = update.effective_user
    database.add_user_if_not_exists(user.id, user.first_name, user.username)

    user_info = (
        f"<b>Informasi Profil Anda:</b>\n"
        f"-----------------------------------\n"
        f"<b>ID Pengguna:</b> <code>{user.id}</code>\n"
        f"<b>Nama Depan:</b> {user.first_name}\n"
        f"<b>Username:</b> @{user.username or 'Tidak ada'}\n"
        f"-----------------------------------\n\n"
        "Gunakan /menu untuk melihat semua fitur."
    )
    await update.message.reply_text(user_info, parse_mode='HTML')


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fungsi untuk perintah /menu."""
    await update.message.reply_text(
        text="Silakan pilih menu di bawah ini:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fungsi untuk perintah /admin (khusus admin)."""
    if not is_admin(update):
        await update.message.reply_text("Perintah ini hanya untuk Admin.")
        return
    await update.message.reply_text(f"Selamat datang di Panel Admin, {update.effective_user.first_name}!")


# --- HANDLER UNTUK TOMBOL ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menangani klik tombol dan memulai conversation jika perlu."""
    query = update.callback_query
    await query.answer()
    command = query.data

    if command == "ssh_add":
        await query.edit_message_text(text="Silakan masukkan <b>Username</b> untuk akun baru:", parse_mode='HTML')
        return GET_USERNAME # Memulai conversation

    # Logika untuk tombol lain tetap di sini...
    elif command == "back_to_main_menu":
        await query.edit_message_text(text="Anda kembali ke menu utama.", reply_markup=keyboards.get_main_menu_keyboard())
    elif command == "menu_ssh":
        await query.edit_message_text(text="<b>SSH PANEL MENU</b>", reply_markup=keyboards.get_ssh_menu_keyboard(), parse_mode='HTML')
    else:
        await query.edit_message_text(text=f"Fitur <b>{command}</b> sedang dalam pengembangan.", parse_mode='HTML')

    return ConversationHandler.END # Akhiri jika bukan tombol memulai conversation


# --- FUNGSI-FUNGSI DALAM CONVERSATION ---

async def get_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima username dan meminta password."""
    username = update.message.text
    # Validasi username (hanya huruf kecil, angka, 4-12 karakter)
    if not re.match("^[a-z0-9]{4,12}$", username):
        await update.message.reply_text("❌ Username tidak valid.\nHarus 4-12 karakter dan hanya berisi huruf kecil dan angka. Silakan coba lagi.")
        return GET_USERNAME

    context.user_data['ssh_username'] = username
    await update.message.reply_text("✅ Username diterima. Sekarang masukkan <b>Password</b>:", parse_mode='HTML')
    return GET_PASSWORD


async def get_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima password dan meminta masa aktif."""
    context.user_data['ssh_password'] = update.message.text
    await update.message.reply_text("✅ Password diterima. Sekarang masukkan <b>Masa Aktif</b> (dalam hari, contoh: 30):", parse_mode='HTML')
    return GET_DURATION


async def get_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima masa aktif dan meminta limit IP."""
    duration = update.message.text
    if not duration.isdigit() or not 1 <= int(duration) <= 365:
        await update.message.reply_text("❌ Masa aktif tidak valid. Masukkan angka antara 1 dan 365.")
        return GET_DURATION

    context.user_data['ssh_duration'] = duration
    await update.message.reply_text("✅ Masa aktif diterima. Terakhir, masukkan <b>Limit IP/Login</b> (contoh: 1):", parse_mode='HTML')
    return GET_IP_LIMIT


async def get_ip_limit_and_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Menerima limit IP, membuat akun, dan mengakhiri conversation."""
    ip_limit = update.message.text
    if not ip_limit.isdigit() or not 1 <= int(ip_limit) <= 10:
        await update.message.reply_text("❌ Limit IP tidak valid. Masukkan angka antara 1 dan 10.")
        return GET_IP_LIMIT

    context.user_data['ssh_ip_limit'] = ip_limit

    # Kirim pesan tunggu
    await update.message.reply_text("⏳ Sedang memproses pembuatan akun, mohon tunggu...")

    # Ambil semua data dari context
    username = context.user_data['ssh_username']
    password = context.user_data['ssh_password']
    duration = context.user_data['ssh_duration']

    # Jalankan skrip backend
    try:
        process = subprocess.run(
            ['sudo', '/opt/hokage-bot/create_ssh_user.sh', username, password, duration, ip_limit],
            capture_output=True, text=True, check=True
        )
        # Kirim output dari skrip ke pengguna
        await update.message.reply_text(process.stdout, parse_mode='HTML')

    except subprocess.CalledProcessError as e:
        # Jika skrip mengembalikan error (misal: username sudah ada)
        await update.message.reply_text(f"❌ Gagal membuat akun:\n<pre>{e.stdout or 'Error tidak diketahui dari skrip.'}</pre>", parse_mode='HTML')
    except Exception as e:
        # Jika ada error lain
        await update.message.reply_text(f"❌ Terjadi kesalahan fatal: {e}")

    # Bersihkan data dan akhiri conversation
    context.user_data.clear()
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Membatalkan dan mengakhiri conversation."""
    await update.message.reply_text("Proses pembuatan akun dibatalkan.")
    context.user_data.clear()
    return ConversationHandler.END
