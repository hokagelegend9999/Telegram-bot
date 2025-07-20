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
import config
import handlers
import database

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors in the telegram bot."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)
    
    # Notify user about error
    if update.effective_message:
        text = (
            "⚠️ Terjadi kesalahan saat memproses permintaan Anda. "
            "Silakan coba lagi atau hubungi admin."
        )
        await update.effective_message.reply_text(text)

def main() -> None:
    """Start the bot."""
    # Initialize database
    database.init_db()
    
    # Create the Application
    application = Application.builder().token(config.BOT_TOKEN).build()
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Conversation handler for main menu and account creation flows
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("menu", handlers.menu)],
        states={
            handlers.ROUTE: [CallbackQueryHandler(handlers.route_handler)],
            handlers.SSH_GET_USERNAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_username)
            ],
            handlers.SSH_GET_PASSWORD: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_password)
            ],
            handlers.SSH_GET_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_duration)
            ],
            handlers.SSH_GET_IP_LIMIT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_ip_limit_and_create)
            ],
            handlers.VMESS_GET_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_user)
            ],
            handlers.VMESS_GET_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_duration)
            ],
            handlers.VLESS_GET_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_user)
            ],
            handlers.VLESS_GET_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_duration)
            ],
            handlers.TROJAN_GET_USER: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_user)
            ],
            handlers.TROJAN_GET_DURATION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_duration)
            ],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CommandHandler("menu", handlers.back_to_menu_from_conv)
        ],
    )
    
    # Add handlers
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("start", handlers.start))
    
    # Start the bot
    logger.info("Bot started and running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
