# keyboards.py (Ganti isi file dengan ini)

from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
import config # Impor config untuk mengakses ADMIN_TELEGRAM_ID

# --- Reply Keyboards (Tombol di bawah) ---

def get_user_main_menu(user_id: int):
    """Menghasilkan menu utama berdasarkan ID user."""
    # Keyboard dasar untuk semua user
    user_menu = [
        ["🛒 Beli Layanan", "👤 Akun Saya"],
        ["💰 Cek Saldo", "➕ Top Up Saldo"],
        ["ℹ️ Bantuan"]
    ]
    # Jika user adalah admin utama, tambahkan tombol untuk kembali
    if user_id == config.ADMIN_TELEGRAM_ID:
        user_menu.append(["👑 Kembali ke Menu Admin"])
        
    return ReplyKeyboardMarkup(user_menu, resize_keyboard=True)


ADMIN_MAIN_MENU = ReplyKeyboardMarkup([
    ["📊 Dashboard", "👥 Manajemen User"],
    ["➕ Top Up Manual", "👤 Switch ke Mode User"],
    ["⚙️ Pengaturan"]
], resize_keyboard=True)


# --- Inline Keyboards (Tombol di dalam pesan) ---

def buy_service_menu():
    # Harga diambil dari config agar dinamis
    keyboard = [[InlineKeyboardButton(f"🔒 SSH Account (Rp {config.SSH_PRICE:,})", callback_data="buy_ssh")]]
    return InlineKeyboardMarkup(keyboard)
