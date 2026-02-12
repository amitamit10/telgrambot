import logging
import threading
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import BOT_TOKEN
from commands import (
    start, ping, status, system, network, storage, services,
    reboot, shutdown, get_logs, list_users, save_contact, button_handler
)
from terminal import terminal_listener

# ─── Logging ──────────────────────────────────────────────────────────
file_handler = logging.FileHandler("bot.log")
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter("%(levelname)s - %(message)s"))

logging.basicConfig(level=logging.INFO, handlers=[file_handler, console_handler])
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram").setLevel(logging.WARNING)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ── Command Handlers ──────────────────────────────────────────────
    app.add_handler(CommandHandler("start",    start))
    app.add_handler(CommandHandler("ping",     ping))
    app.add_handler(CommandHandler("status",   status))
    app.add_handler(CommandHandler("system",   system))
    app.add_handler(CommandHandler("network",  network))
    app.add_handler(CommandHandler("storage",  storage))
    app.add_handler(CommandHandler("services", services))

    # Admin commands
    app.add_handler(CommandHandler("reboot",   reboot))
    app.add_handler(CommandHandler("shutdown", shutdown))
    app.add_handler(CommandHandler("log",      get_logs))
    app.add_handler(CommandHandler("list",     list_users))

    # ── Inline Button Handler ─────────────────────────────────────────
    app.add_handler(CallbackQueryHandler(button_handler))

    # ── Text → Register name ──────────────────────────────────────────
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), save_contact))

    # ── Terminal Panel ────────────────────────────────────────────────
    threading.Thread(target=terminal_listener, daemon=True).start()

    app.run_polling()


if __name__ == "__main__":
    main()