# main.py (Versi Final Stabil)
import logging
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ConversationHandler, MessageHandler, filters
)
import config, handlers, database

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

def main() -> None:
    database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # --- SATU CONVERSATION HANDLER UTAMA ---
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", handlers.menu)],
        states={
            handlers.ROUTE: [CallbackQueryHandler(handlers.route_handler)],
            
            # Alur SSH
            handlers.SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_username)],
            handlers.SSH_GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_password)],
            handlers.SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_duration)],
            handlers.SSH_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_ip_limit_and_create)],
            
            # Alur Vmess
            handlers.VMESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_user)],
            handlers.VMESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_duration)],
            handlers.VMESS_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_ip_limit)],
            handlers.VMESS_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_quota_and_create)],
            
            # Alur Vless
            handlers.VLESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_user)],
            handlers.VLESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_duration)],
            handlers.VLESS_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_ip_limit)],
            handlers.VLESS_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_quota_and_create)],
            
            # Alur Trojan
            handlers.TROJAN_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_user)],
            handlers.TROJAN_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_duration)],
            handlers.TROJAN_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_ip_limit)],
            handlers.TROJAN_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_quota_and_create)],
        },
        fallbacks=[CommandHandler('cancel', handlers.cancel)],
        allow_reentry=True
    )

    # --- Daftarkan semua handler ---
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("admin", handlers.admin))
    
    # Handler ini akan menangani semua klik tombol di luar percakapan
    application.add_handler(CallbackQueryHandler(handlers.route_handler))
    
    logging.info("Bot siap dan mulai berjalan...")
    application.run_polling()

if __name__ == "__main__":
    main()
