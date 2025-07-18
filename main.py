# main.py
import logging
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
import config, handlers

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main() -> None:
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CallbackQueryHandler(handlers.button_handler))
    logging.info("Bot siap dan mulai berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
