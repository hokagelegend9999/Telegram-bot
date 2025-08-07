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

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Menangani semua error yang tidak tertangkap."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        text = "⚠️ Terjadi kesalahan internal. Silakan coba lagi atau hubungi admin."
        try:
            await update.effective_message.reply_text(text)
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")

def main() -> None:
    """Memulai dan menjalankan bot."""
    database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_error_handler(error_handler)

    # ==================================================================
    #   INTI PERBAIKAN: Menggabungkan semua state ke dalam SATU ConversationHandler
    # ==================================================================
    
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", handlers.start),
            CommandHandler("menu", handlers.menu),
            # Jadikan route_handler sebagai entry point utama untuk tombol
            # Ini akan menangani SEMUA tombol di awal percakapan
            CallbackQueryHandler(handlers.route_handler)
        ],
        states={
            # State Awal (ROUTE)
            # Di state ini, bot hanya mendengarkan tombol (CallbackQuery)
            handlers.ROUTE: [
                CallbackQueryHandler(handlers.route_handler)
            ],

            # --- State untuk Pembuatan Akun ---
            handlers.SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_username)],
            handlers.SSH_GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_password)],
            handlers.SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_duration)],
            handlers.SSH_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_ip_limit_and_create)],

            handlers.VMESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_user)],
            handlers.VMESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_duration)],

            handlers.VLESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_user)],
            handlers.VLESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_duration)],
            handlers.VLESS_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_ip_limit)],
            handlers.VLESS_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_quota_and_create)],

            handlers.TROJAN_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_user)],
            handlers.TROJAN_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_duration)],
            handlers.TROJAN_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_ip_limit)],
            handlers.TROJAN_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_quota_and_create)],

            # --- State untuk Perpanjangan Akun ---
            handlers.RENEW_SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_ssh_get_username)],
            handlers.RENEW_SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_ssh_get_duration_and_execute)],
            handlers.RENEW_VMESS_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_vmess_get_username)],
            handlers.RENEW_VMESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_vmess_get_duration_and_execute)],

            # --- State untuk Akun Trial ---
            handlers.TRIAL_CREATE_SSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_ssh_trial_account)],
            handlers.TRIAL_CREATE_VMESS: [MessageHandler(filters.ALL, handlers.create_vmess_trial_account)], # Sesuai kode asli
            handlers.TRIAL_CREATE_VLESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_vless_trial_account)],
            handlers.TRIAL_CREATE_TROJAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_trojan_trial_account)],

            # --- State untuk Hapus Akun ---
            handlers.DELETE_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.delete_get_username)],
            handlers.DELETE_CONFIRMATION: [CallbackQueryHandler(handlers.delete_confirmation, pattern="^(confirm_proceed|cancel_action)$")],

            # --- State untuk Melihat List/Config ---
            handlers.SSH_SELECT_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_select_account_and_show_config)],
            handlers.VMESS_SELECT_ACCOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_select_account_and_show_config)],
        },
        fallbacks=[
            CommandHandler("start", handlers.start),
            CommandHandler("menu", handlers.menu),
            CommandHandler("cancel", handlers.cancel),
            # Tombol kembali ke menu sekarang juga bagian dari fallback
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        # Ini penting agar state tidak hilang setelah callback query
        per_message=False,
        per_user=True,
        per_chat=False,
        # Beri nama agar bisa dibatalkan dari mana saja
        name="main_conversation",
        persistent=False
    )

    # Cukup tambahkan SATU handler utama ini
    application.add_handler(conv_handler)

    logger.info("Bot started and running with unified conversation handler...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
