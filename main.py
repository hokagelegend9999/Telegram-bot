# main.py (Versi baru dengan handler terpisah)
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import config, handlers, database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main() -> None:
    database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()

    # --- Mendaftarkan setiap perintah ke fungsinya masing-masing ---
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("menu", handlers.menu))
    application.add_handler(CommandHandler("admin", handlers.admin))

    # Handler untuk semua klik tombol.
    application.add_handler(CallbackQueryHandler(handlers.button_handler))

    logging.info("Bot siap dan mulai berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
