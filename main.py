# main.py (Versi baru dengan ConversationHandler)
import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters
)
import config, handlers, database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main() -> None:
    database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()

    # --- Conversation Handler untuk Membuat Akun SSH ---
    ssh_creation_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.button_handler, pattern='^ssh_add$')],
        states={
            handlers.GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_username)],
            handlers.GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_password)],
            handlers.GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_duration)],
            handlers.GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.get_ip_limit_and_create)],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
    )

    # --- Daftarkan semua handler ---
    application.add_handler(ssh_creation_conv) # Daftarkan conversation dulu

    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("menu", handlers.menu))
    application.add_handler(CommandHandler("admin", handlers.admin))

    # Handler untuk tombol lain yang tidak memulai conversation
    application.add_handler(CallbackQueryHandler(handlers.button_handler))

    logging.info("Bot siap dan mulai berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
