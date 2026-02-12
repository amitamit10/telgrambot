import threading
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import BOT_TOKEN
from commands import (
    start, ping, status, system, network, storage, services,
    reboot, shutdown, get_logs, list_users, save_contact
)
from terminal import terminal_listener  # אופציונלי לניהול בזמן אמת

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ------------------- Command Handlers -------------------
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("system", system))
    app.add_handler(CommandHandler("network", network))
    app.add_handler(CommandHandler("storage", storage))
    app.add_handler(CommandHandler("services", services))

    # Admin commands
    app.add_handler(CommandHandler("reboot", reboot))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("log", get_logs))
    app.add_handler(CommandHandler("list", list_users))

    # User identification
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), save_contact))

    # ------------------- Terminal Listener -------------------
    threading.Thread(target=terminal_listener, daemon=True).start()

    print("🤖 Server Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
