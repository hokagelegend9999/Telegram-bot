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

    # --- Command Handlers ---
    # Perintah /start dan /menu selalu harus bisa diakses.
    application.add_handler(CommandHandler("start", handlers.start))
    application.add_handler(CommandHandler("menu", handlers.menu))
    application.add_handler(CommandHandler("cancel", handlers.cancel)) # Global cancel command untuk mengakhiri konversasi apapun

    # --- ConversationHandlers untuk Alur Multi-Langkah (PENTING: Definisikan ini DULU) ---
    # ConversationHandler akan "mencegat" callback query yang sesuai dengan entry_points-nya
    # sebelum CallbackQueryHandler global di bawahnya. Ini penting untuk prioritas.

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
        map_to_parent={handlers.ROUTE: handlers.ROUTE}, # Kembali ke ROUTE utama setelah selesai
        per_user=True, per_chat=False # Pengaturan per_user/per_chat untuk ConversationHandler
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
            handlers.TRIAL_CREATE_VMESS: [MessageHandler(filters.ALL, handlers.create_vmess_trial_account)], # <--- Perubahan filter untuk debugging
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
            # HANYA ketika bot berada dalam state DELETE_CONFIRMATION, sehingga tidak bentrok dengan route_handler
            # saat bot TIDAK dalam konversasi penghapusan.
            handlers.DELETE_CONFIRMATION: [CallbackQueryHandler(handlers.delete_confirmation, pattern="^(confirm_proceed|cancel_action)$")]
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE},
        per_user=True, per_chat=False
    ))

    # 10. VMESS List & View Config Conversation (BARU)
    application.add_handler(ConversationHandler(
        entry_points=[CallbackQueryHandler(handlers.route_handler, pattern="^vmess_list$")], # Memulai alur list VMESS
        states={
            # State ini menunggu input nomor akun dari pengguna
            handlers.VMESS_SELECT_ACCOUNT: [MessageHandler(filters.ALL, handlers.vmess_select_account_and_show_config)], # <--- Perubahan filter untuk debugging
        },
        fallbacks=[
            CommandHandler("cancel", handlers.cancel),
            CallbackQueryHandler(handlers.back_to_menu_from_conv, pattern="^main_menu$")
        ],
        map_to_parent={handlers.ROUTE: handlers.ROUTE}, # Kembali ke ROUTE utama setelah selesai
        per_user=True, per_chat=False
    ))


    # --- CallbackQueryHandlers Global (Definisikan ini SETELAH semua ConversationHandler) ---
    # Ini akan menangani semua CallbackQuery yang tidak ditangkap oleh ConversationHandler di atas.
    # Termasuk navigasi menu utama, dan tombol tools (yang tidak memulai konversasi multi-langkah).
    # Callback data 'confirm_proceed' dan 'cancel_action' di sini hanya untuk ALUR TOOLS (reboot, restore).
    # 'ssh_list', 'vless_list', 'trojan_list' tetap di sini karena belum diubah menjadi interaktif.
    application.add_handler(CallbackQueryHandler(handlers.route_handler, pattern="^(main_menu|back_to_main_menu|menu_ssh|menu_vmess|menu_vless|menu_trojan|menu_tools|ssh_list|vless_list|trojan_list|menu_running|menu_restart|menu_backup|confirm_restore|reboot_server|trial_cleanup|confirm_proceed|cancel_action)$"))

    # Jalankan bot
    logger.info("Bot started and running...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
