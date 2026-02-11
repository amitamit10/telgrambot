import threading
from telegram.ext import ApplicationBuilder, CommandHandler
from config import BOT_TOKEN
from terminal import terminal_listener
from commands import start, status, ping, system, network, storage, services

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CommandHandler("system", system))
    app.add_handler(CommandHandler("network", network))
    app.add_handler(CommandHandler("storage", storage))
    app.add_handler(CommandHandler("services", services))

    threading.Thread(target=terminal_listener, daemon=True).start()

    print("🤖 Server Bot running...")
    app.run_polling()


if __name__ == "__main__":
    main()
