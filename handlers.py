# File: handlers.py
# Versi baru dengan fungsi terpisah untuk setiap perintah.

from telegram import Update
from telegram.ext import ContextTypes
import keyboards, config, database

# --- FUNGSI BANTUAN ---
def is_admin(update: Update) -> bool:
    """Memeriksa apakah pengguna adalah admin utama."""
    return update.effective_user.id == config.ADMIN_TELEGRAM_ID

# --- HANDLER UNTUK PERINTAH ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Fungsi untuk perintah /start."""
    user = update.effective_user
    database.add_user_if_not_exists(user.id, user.first_name, user.username)

    await update.message.reply_text(
        f"Selamat datang, {user.first_name}!\n"
        "Ini adalah pesan selamat datang. Gunakan /menu untuk melihat menu."
    )

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

    admin_name = update.effective_user.first_name
    await update.message.reply_text(f"Selamat datang di Panel Admin, {admin_name}!")
    # Di sini Anda bisa menambahkan keyboard atau logika khusus admin

# --- HANDLER UNTUK SEMUA TOMBOL ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # Kode button_handler Anda yang sudah ada biarkan di sini
    # ... (tidak perlu diubah) ...
    query = update.callback_query
    await query.answer()
    command = query.data

    if command == "back_to_main_menu":
        await query.edit_message_text(
            text="Anda kembali ke menu utama. Silakan pilih:",
            reply_markup=keyboards.get_main_menu_keyboard()
        )
    elif command == "menu_ssh":
        await query.edit_message_text(
            text="<b>SSH PANEL MENU</b>\n\nSilakan pilih salah satu opsi:",
            reply_markup=keyboards.get_ssh_menu_keyboard(),
            parse_mode='HTML'
        )
    # ... dan seterusnya untuk semua tombol ...
    else:
         await query.edit_message_text(text=f"Anda memilih: {command}")
