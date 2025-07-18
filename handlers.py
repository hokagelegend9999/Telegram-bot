# File: handlers.py
# Versi lengkap dengan logika menu, sub-menu, dan perintah admin.

import subprocess
from telegram import Update
from telegram.ext import ContextTypes

# Impor dari file lokal Anda
import keyboards
import config
import database

# --- FUNGSI BANTUAN ---
def is_admin(update: Update) -> bool:
    """Memeriksa apakah pengguna adalah admin utama."""
    return update.effective_user.id == config.ADMIN_TELEGRAM_ID


# --- HANDLER UNTUK PERINTAH ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mengirim menu utama saat user mengirim /start."""
    user = update.effective_user
    # Menambahkan user ke database jika belum ada
    database.add_user_if_not_exists(user.id, user.first_name, user.username)
    
    await update.message.reply_text(
        text="Selamat datang! Silakan pilih menu di bawah ini:",
        reply_markup=keyboards.get_main_menu_keyboard()
    )

async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Perintah khusus yang hanya bisa diakses oleh admin."""
    if not is_admin(update):
        await update.message.reply_text("Anda tidak memiliki hak akses untuk perintah ini.")
        return

    # Kirim pesan atau menu khusus untuk admin
    admin_name = update.effective_user.first_name
    await update.message.reply_text(f"Selamat datang di Panel Admin, {admin_name}!")
    # Di sini Anda bisa menambahkan keyboard khusus admin jika perlu


# --- HANDLER UNTUK SEMUA TOMBOL ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Satu fungsi untuk menangani semua klik tombol inline."""
    query = update.callback_query
    await query.answer()  # Wajib untuk konfirmasi klik
    command = query.data

    # --- NAVIGASI ANTAR MENU ---
    if command == "back_to_main_menu":
        await query.edit_message_text(
            text="Anda kembali ke menu utama. Silakan pilih:",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
        return

    # --- LOGIKA MENU UTAMA ---
    if command == "menu_ssh":
        await query.edit_message_text(
            text="<b>SSH PANEL MENU</b>\n\nSilakan pilih salah satu opsi:",
            reply_markup=keyboards.get_ssh_menu_keyboard(),
            parse_mode='HTML'
        )
    elif command == "menu_vmess":
        await query.edit_message_text(text="Fitur VMESS sedang dalam pengembangan.")
    elif command == "menu_vless":
        await query.edit_message_text(text="Fitur VLESS sedang dalam pengembangan.")
    elif command == "menu_trojan":
        await query.edit_message_text(text="Fitur TROJAN sedang dalam pengembangan.")
    elif command == "menu_running":
        # Contoh memanggil skrip backend
        # proses = subprocess.run(['sudo', '/opt/hokage-bot/status-service.sh'], capture_output=True, text=True)
        # await query.edit_message_text(text=f"<b>Status Layanan:</b>\n<pre>{proses.stdout}</pre>", parse_mode='HTML')
        await query.edit_message_text(text="Fitur Cek Status sedang dalam pengembangan.")
    elif command == "menu_restart":
        await query.edit_message_text(text="Fitur Restart Layanan sedang dalam pengembangan.")
    elif command == "menu_reboot":
        await query.edit_message_text(text="Fitur Reboot Server sedang dalam pengembangan.")
    elif command == "menu_update":
        await query.edit_message_text(text="Fitur Update Skrip sedang dalam pengembangan.")
    elif command == "menu_backup":
        await query.edit_message_text(text="Fitur Backup sedang dalam pengembangan.")
    elif command == "menu_setting":
        await query.edit_message_text(text="Fitur Setting sedang dalam pengembangan.")
    elif command == "close_menu":
        await query.edit_message_text(text="Menu ditutup. Kirim /start untuk membuka lagi.")

    # --- LOGIKA SUB-MENU SSH ---
    elif command == "ssh_add":
        await query.edit_message_text(text="Memulai proses penambahan akun SSH...")
    elif command == "ssh_trial":
        await query.edit_message_text(text="Memulai proses pembuatan akun trial...")
    elif command == "ssh_renew":
        await query.edit_message_text(text="Memulai proses perpanjangan akun...")
    elif command == "ssh_delete":
        await query.edit_message_text(text="Memulai proses penghapusan akun...")
    elif command == "ssh_online":
        await query.edit_message_text(text="Memeriksa pengguna SSH yang online...")
    elif command == "ssh_config":
        await query.edit_message_text(text="Memeriksa konfigurasi pengguna...")
    elif command == "ssh_limit":
        await query.edit_message_text(text="Mengubah limit IP...")
    elif command == "ssh_lock":
        await query.edit_message_text(text="Mengunci login pengguna...")
    elif command == "ssh_unlock":
        await query.edit_message_text(text="Membuka kunci login pengguna...")
