# File: main.py
import logging
from telegram.ext import Application, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import config, handlers, database

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logging.getLogger("httpx").setLevel(logging.WARNING)

def main() -> None:
    database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", handlers.menu)],
        states={
            handlers.ROUTE: [CallbackQueryHandler(handlers.route_handler)],
            handlers.SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_username)],
            handlers.SSH_GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_password)],
            handlers.SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_duration)],
            handlers.SSH_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_ip_limit_and_create)],
            handlers.VMESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_user)],
            handlers.VMESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_duration)],
            handlers.VLESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_user)],
            handlers.VLESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_duration)],
            handlers.TROJAN_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_user)],
            handlers.TROJAN_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_duration)],
        },
        fallbacks=[CommandHandler("cancel", handlers.cancel), CommandHandler("menu", handlers.back_to_menu_from_conv)]
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", handlers.start))
    
    logging.info("Bot siap dan mulai berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
