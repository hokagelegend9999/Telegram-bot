import logging
from telegram import Update
from telegram.ext import (
    Application,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    ContextTypes
)

# (Disarankan) Import token dan konfigurasi lain dari config.py
import config

# Import semua handler dan state yang dibutuhkan dari handlers.py
import handlers
import database

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani semua error yang tidak tertangkap."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Kirim pesan error ke user jika memungkinkan
    if isinstance(update, Update) and update.effective_message:
        text = "⚠️ Terjadi kesalahan internal. Silakan coba lagi atau hubungi admin."
        await update.effective_message.reply_text(text)

def main() -> None:
    """Memulai dan menjalankan bot."""
    # Inisialisasi database
    database.init_db()

    # Buat Application builder
    application = Application.builder().token(config.BOT_TOKEN).build()

    # Tambahkan error handler
    application.add_error_handler(error_handler)

    # ConversationHandler utama yang mengatur semua alur bot
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.start),
            CommandHandler("menu", handlers.menu),
            # Menjadikan semua tombol sebagai entry point utama
            CallbackQueryHandler(handlers.route_handler)
        ],
        states={
            # State utama, menunggu input dari tombol menu
            handlers.ROUTE: [
                CallbackQueryHandler(handlers.route_handler)
            ],

            # --- Alur Pembuatan Akun ---
            # SSH
            handlers.SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_username)],
            handlers.SSH_GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_password)],
            handlers.SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_duration)],
            handlers.SSH_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_ip_limit_and_create)],
            
            # VMESS
            handlers.VMESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_user)],
            handlers.VMESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_duration)],

            # VLESS (Pastikan handler-nya ada di handlers.py)
            handlers.VLESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_user)],
            handlers.VLESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_duration)],
            handlers.VLESS_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_ip_limit)],
            handlers.VLESS_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_quota_and_create)],

            # TROJAN (Pastikan handler-nya ada di handlers.py)
            handlers.TROJAN_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_user)],
            handlers.TROJAN_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_duration)],
            handlers.TROJAN_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_ip_limit)],
            handlers.TROJAN_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_quota_and_create)],

            # --- Alur Perpanjangan Akun (YANG BARU DITAMBAHKAN) ---
            handlers.RENEW_SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_ssh_get_username)],
            handlers.RENEW_SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_ssh_get_duration_and_execute)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CommandHandler("menu", handlers.menu) # /menu bisa membatalkan dan kembali ke menu
        ],
        # Agar state tidak hangus jika user lama membalas
        conversation_timeout=600, # Timeout dalam 10 menit
        # Memungkinkan handler di luar state ini (misal: tombol menu) bisa diakses
        per_user=True,
        per_chat=True
    )

    # Daftarkan handler utama
    application.add_handler(conv_handler)

    # Jalankan bot
    logger.info("Bot started and running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
