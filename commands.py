# commands.py
import psutil
import platform
import shutil
import subprocess
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from auth import is_authorized

# START
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(
            f"🚫 Access denied.\nYour ID: {chat_id}"
        )
        return

    await update.message.reply_text(
        "🚀 Server Bot Active\n\n"
        "Available commands:\n"
        "/status - Show basic server stats\n"
        "/ping - Check bot is alive\n"
        "/system - CPU/RAM top processes\n"
        "/network - Network usage and connections\n"
        "/storage - Disk usage\n"
        "/services - Check system services\n"
    )


# STATUS
async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(f"Your ID: {chat_id}")
        return

    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime = datetime.now() - datetime.fromtimestamp(psutil.boot_time())

    message = (
        "🖥 *Server Status*\n\n"
        f"OS: `{platform.system()} {platform.release()}`\n"
        f"CPU: `{cpu}%`\n"
        f"RAM: `{ram.percent}%`\n"
        f"Disk: `{disk.percent}%`\n"
        f"Uptime: `{str(uptime).split('.')[0]}`\n"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


# ===== PING =====
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(f"Your ID: {chat_id}")
        return
    await update.message.reply_text("🏓 Pong!")


# SYSTEM
async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(f"Your ID: {chat_id}")
        return

    processes = []
    for p in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes.append(p.info)
        except:
            pass

    top_cpu = sorted(processes, key=lambda x: x['cpu_percent'], reverse=True)[:3]
    top_ram = sorted(processes, key=lambda x: x['memory_percent'], reverse=True)[:3]

    message = "🧠 *System Overview*\n\n"
    message += "🔥 Top CPU:\n"
    for p in top_cpu:
        message += f"{p['name']} - {p['cpu_percent']}%\n"

    message += "\n💾 Top RAM:\n"
    for p in top_ram:
        message += f"{p['name']} - {round(p['memory_percent'],1)}%\n"

    message += f"\n📦 Total Processes: {len(psutil.pids())}"

    await update.message.reply_text(message, parse_mode="Markdown")


# NETWORK
async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(f"Your ID: {chat_id}")
        return

    net = psutil.net_io_counters()
    connections = len(psutil.net_connections())

    message = (
        "🌐 *Network Overview*\n\n"
        f"Connections: {connections}\n"
        f"Upload: {round(net.bytes_sent/1e6,2)} MB\n"
        f"Download: {round(net.bytes_recv/1e6,2)} MB\n"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


# STORAGE
async def storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(f"Your ID: {chat_id}")
        return

    total, used, free = shutil.disk_usage("/")
    message = (
        "💾 *Storage*\n\n"
        f"Total: {round(total/1e9,2)} GB\n"
        f"Used: {round(used/1e9,2)} GB\n"
        f"Free: {round(free/1e9,2)} GB\n"
    )

    await update.message.reply_text(message, parse_mode="Markdown")


#SERVICES
def check_service(name):
    try:
        subprocess.check_output(["systemctl", "is-active", "--quiet", name])
        return "🟢"
    except:
        return "🔴"

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not is_authorized(chat_id):
        await update.message.reply_text(f"Your ID: {chat_id}")
        return

    message = (
        "⚙ *Services*\n\n"
        f"SSH: {check_service('ssh')}\n"
        f"Nginx: {check_service('nginx')}\n"
        f"Docker: {check_service('docker')}\n"
        f"MySQL: {check_service('mysql')}\n"
    )

    await update.message.reply_text(message, parse_mode="Markdown")
