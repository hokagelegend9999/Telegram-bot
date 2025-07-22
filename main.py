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
import handlers # Mengimpor semua dari handlers.py
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
        await update.effective_message.reply_text(text)

def main() -> None:
    """Memulai dan menjalankan bot."""
    database.init_db()
    application = Application.builder().token(config.BOT_TOKEN).build()
    application.add_error_handler(error_handler)

    # --- Command Handlers ---
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("menu", handlers.menu))
    application.add_handler(CommandHandler("cancel", handlers.cancel)) # Global cancel command

    # --- CallbackQueryHandlers untuk Menu Navigasi Utama dan Tools (yang tidak memulai konv) ---
    # Pola di sini harus spesifik untuk tombol menu utama dan tombol tools tertentu.
    # Hindari pola 'confirm_proceed' dan 'cancel_action' agar tidak bentrok dengan ConversationHandler.
    # 'confirm_proceed' dan 'cancel_action' untuk tools sekarang ditangani di dalam route_handler.
    application.add_handler(CallbackQueryHandler(handlers.route_handler, pattern="^(main_menu|back_to_main_menu|menu_ssh|menu_vmess|menu_vless|menu_trojan|menu_tools|menu_running|menu_restart|menu_backup|confirm_restore|reboot_server|trial_cleanup|confirm_proceed|cancel_action)$"))


    # --- CallbackQueryHandlers untuk Aksi Sekali Jalan (List) ---
    application.add_handler(CallbackQueryHandler(handlers.ssh_list_accounts, pattern="^ssh_list$"))
    application.add_handler(CallbackQueryHandler(handlers.vmess_list_accounts, pattern="^vmess_list$"))
    application.add_handler(CallbackQueryHandler(handlers.vless_list_accounts, pattern="^vless_list$"))
    application.add_handler(CallbackQueryHandler(handlers.trojan_list_accounts, pattern="^trojan_list$"))


    # --- ConversationHandlers untuk Alur Multi-Langkah (Create, Renew, Trial, Delete) ---

    # 1. SSH Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^ssh_add$")],
        states={
            handlers.SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_username)],
            handlers.SSH_GET_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_password)],
            handlers.SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_duration)],
            handlers.SSH_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.ssh_get_ip_limit_and_create)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 2. SSH Renewal Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^ssh_renew$")],
        states={
            handlers.RENEW_SSH_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_ssh_get_username)],
            handlers.RENEW_SSH_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.renew_ssh_get_duration_and_execute)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 3. VMESS Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^vmess_add$")],
        states={
            handlers.VMESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_user)],
            handlers.VMESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vmess_get_duration)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))
    
    # 4. VMESS Trial Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^vmess_trial$")],
        states={
            handlers.TRIAL_CREATE_VMESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_vmess_trial_account)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 5. VLESS Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^vless_add$")],
        states={
            handlers.VLESS_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_user)],
            handlers.VLESS_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_duration)],
            handlers.VLESS_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_ip_limit)],
            handlers.VLESS_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.vless_get_quota_and_create)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 6. VLESS Trial Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^vless_trial$")],
        states={
            handlers.TRIAL_CREATE_VLESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_vless_trial_account)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 7. TROJAN Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^trojan_add$")],
        states={
            handlers.TROJAN_GET_USER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_user)],
            handlers.TROJAN_GET_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_duration)],
            handlers.TROJAN_GET_IP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_ip_limit)],
            handlers.TROJAN_GET_QUOTA: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.trojan_get_quota_and_create)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 8. TROJAN Trial Creation Conversation
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^trojan_trial$")],
        states={
            handlers.TRIAL_CREATE_TROJAN: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.create_trojan_trial_account)],
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 9. Delete Account Conversation (Generik untuk semua jenis akun)
    # Ini akan mengambil alih penanganan 'confirm_proceed' dan 'cancel_action'
    # ketika bot berada dalam state DELETE_CONFIRMATION.
    application.add_handler(ConversationHandler(
        entry_points=[
            CallbackQueryHandler(handlers.route_handler, pattern="^ssh_delete$"),
            CallbackQueryHandler(handlers.route_handler, pattern="^vmess_delete$"),
            CallbackQueryHandler(handlers.route_handler, pattern="^vless_delete$"),
            CallbackQueryHandler(handlers.route_handler, pattern="^trojan_delete$")
        ],
        states={
            handlers.DELETE_GET_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.delete_get_username)],
            # Penting: CallbackQueryHandler ini akan menangkap 'confirm_proceed' dan 'cancel_action'
            # HANYA ketika dalam state DELETE_CONFIRMATION, sehingga tidak bentrok dengan route_handler.
            handlers.DELETE_CONFIRMATION: [CallbackQueryHandler(handlers.delete_confirmation, pattern="^(confirm_proceed|cancel_action)$")]
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # Jalankan bot
    logger.info("Bot started and running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
