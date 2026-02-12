import psutil
import os
import logging
from telegram import Update
from telegram.ext import ContextTypes
from auth import is_authorized, is_admin

LOG_FILE = "bot.log"  # שם קובץ הלוג שלך

# ----------------- Users DB -----------------
users_db = {}  # {user_id: name}


# ----------------- START -----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # משתמש חדש – מבקש שם להזדהות
    if user_id not in users_db:
        await update.message.reply_text(
            "👋 Hello! Please reply with your name to identify yourself."
        )
        return

    # משתמש רשום – מציג את התפריט
    msg = "🤖 *Server Bot Active*\n\n*Available Commands:*\n\n"
    msg += "📌 /status - Show server stats\n"
    msg += "📌 /ping - Test bot is alive\n"
    msg += "📌 /system - Top CPU/RAM processes\n"
    msg += "📌 /network - Network usage and connections\n"
    msg += "📌 /storage - Disk usage\n"
    msg += "📌 /services - Check key services\n"

    msg += "\n💡 Notes:\n"
    msg += "- Regular users: standard commands only\n"
    msg += "- Admins: can use admin commands\n"

    # פקודות אדמין
    if is_admin(user_id):
        msg += "\n⚙️ Admin Commands:\n"
        msg += "/reboot - Reboot server\n"
        msg += "/shutdown - Shutdown server\n"
        msg += "/log - Last 20 log lines\n"
        msg += "/list - Show all users\n"

    await update.message.reply_text(msg, parse_mode="Markdown")


# ----------------- SAVE CONTACT -----------------
async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in users_db:
        users_db[user_id] = text
        await update.message.reply_text(f"✅ Thanks {text}, you are now registered!")


# ----------------- PING -----------------
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"{user_id} used /ping")
    await update.message.reply_text("🏓 Pong!")


# ----------------- STATUS -----------------
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text(f"❌ No access\nID: {user_id}")
        return

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    disk = psutil.disk_usage("/").percent
    uptime = os.popen("uptime -p").read().strip()

    logging.info(f"{user_id} used /status")
    await update.message.reply_text(
        f"📊 Status\nCPU: {cpu}%\nRAM: {ram}%\nDisk: {disk}%\nUptime: {uptime}"
    )


# ----------------- SYSTEM -----------------
async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    processes = sorted(psutil.process_iter(['name','cpu_percent']),
                       key=lambda p: p.info['cpu_percent'], reverse=True)[:5]
    msg = "🔥 Top Processes:\n"
    for p in processes:
        msg += f"{p.info['name']} - {p.info['cpu_percent']}%\n"
    logging.info(f"{user_id} used /system")
    await update.message.reply_text(msg)


# ----------------- NETWORK -----------------
async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    net = psutil.net_io_counters()
    logging.info(f"{user_id} used /network")
    await update.message.reply_text(
        f"🌐 Network Usage\nSent: {round(net.bytes_sent/1e6,2)} MB\nRecv: {round(net.bytes_recv/1e6,2)} MB"
    )


# ----------------- STORAGE -----------------
async def storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    disk = psutil.disk_usage("/")
    logging.info(f"{user_id} used /storage")
    await update.message.reply_text(
        f"💾 Storage\nTotal: {round(disk.total/1e9,2)} GB\nUsed: {round(disk.used/1e9,2)} GB\nFree: {round(disk.free/1e9,2)} GB"
    )


# ----------------- SERVICES -----------------
async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    svcs = ["ssh","nginx","docker"]
    msg = "🛠 Services Status:\n"
    for s in svcs:
        status = os.popen(f"systemctl is-active {s}").read().strip()
        msg += f"{s}: {status}\n"

    logging.info(f"{user_id} used /services")
    await update.message.reply_text(msg)


# ----------------- REBOOT -----------------
async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only\nID: {user_id}")
        return

    await update.message.reply_text("🔄 Rebooting server...")
    os.system("sudo reboot")


# ----------------- SHUTDOWN -----------------
async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only\nID: {user_id}")
        return

    await update.message.reply_text("🛑 Shutting down server...")
    os.system("sudo shutdown now")


# ----------------- LOG -----------------
async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only\nID: {user_id}")
        return

    try:
        with open(LOG_FILE,"r") as f:
            lines = f.readlines()[-20:]
        if not lines:
            await update.message.reply_text("No logs yet.")
            return

        lines.append(f"\nℹ Requested by admin ID: {user_id}\n")
        await update.message.reply_text(f"📜 Last 20 log lines:\n\n{''.join(lines)}")
        logging.info(f"Admin {user_id} requested /log")
    except FileNotFoundError:
        await update.message.reply_text(f"❌ Log file '{LOG_FILE}' not found.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error reading logs: {e}")


# ----------------- LIST USERS -----------------
async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only\nID: {user_id}")
        return

    if not users_db:
        await update.message.reply_text("No users registered yet.")
        return

    msg = "📋 Registered Users:\n"
    for uid, name in users_db.items():
        msg += f"{uid} - {name}\n"

    await update.message.reply_text(msg)
