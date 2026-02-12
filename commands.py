import psutil
import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from auth import is_authorized, is_admin

LOG_FILE = "bot.log"

users_db = {}  # {user_id: name}


# ──────────────────────────────────────────────
#  HELPERS
# ──────────────────────────────────────────────

def bar(percent: float, length: int = 12) -> str:
    """Visual progress bar using block chars."""
    filled = int(length * percent / 100)
    return "█" * filled + "░" * (length - filled)

def status_icon(percent: float) -> str:
    if percent < 60:   return "🟢"
    if percent < 85:   return "🟡"
    return "🔴"

def fmt_bytes(n: float) -> str:
    """Auto-format bytes → KB / MB / GB."""
    if n >= 1e9:  return f"{n/1e9:.1f} GB"
    if n >= 1e6:  return f"{n/1e6:.1f} MB"
    if n >= 1e3:  return f"{n/1e3:.1f} KB"
    return f"{n:.0f} B"

def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    keyboard = [
        [
            InlineKeyboardButton("📊 Status",   callback_data="status"),
            InlineKeyboardButton("🔥 System",   callback_data="system"),
        ],
        [
            InlineKeyboardButton("🌐 Network",  callback_data="network"),
            InlineKeyboardButton("💾 Storage",  callback_data="storage"),
        ],
        [
            InlineKeyboardButton("🛠 Services", callback_data="services"),
            InlineKeyboardButton("🏓 Ping",     callback_data="ping"),
        ],
    ]
    if is_admin(user_id):
        keyboard.append([
            InlineKeyboardButton("📜 Logs",    callback_data="log"),
            InlineKeyboardButton("👥 Users",   callback_data="list"),
        ])
        keyboard.append([
            InlineKeyboardButton("🔄 Reboot",   callback_data="reboot"),
            InlineKeyboardButton("🛑 Shutdown", callback_data="shutdown"),
        ])
    return InlineKeyboardMarkup(keyboard)

def back_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back to Menu", callback_data="menu")]])


# ──────────────────────────────────────────────
#  START
# ──────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if user_id not in users_db:
        await update.message.reply_text(
            "👋 *Welcome!*\n\nPlease reply with your *name* to register.",
            parse_mode="Markdown"
        )
        return

    name = users_db[user_id]
    role = "👑 Admin" if is_admin(user_id) else "👤 User"
    msg = (
        f"🤖 *Server Monitor Bot*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"Hello, *{name}*!  {role}\n\n"
        f"Choose an action from the menu below 👇"
    )
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard(user_id))


# ──────────────────────────────────────────────
#  SAVE CONTACT
# ──────────────────────────────────────────────

async def save_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text.strip()

    if user_id not in users_db:
        users_db[user_id] = text
        await update.message.reply_text(
            f"✅ *Registered successfully!*\n\n"
            f"👤 Name: *{text}*\n"
            f"🪪 Your ID: `{user_id}`\n\n"
            f"Send /start to open the menu.",
            parse_mode="Markdown"
        )


# ──────────────────────────────────────────────
#  PING
# ──────────────────────────────────────────────

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"{user_id} used /ping")
    await update.message.reply_text("🏓 *Pong!* Bot is alive.", parse_mode="Markdown")


# ──────────────────────────────────────────────
#  STATUS
# ──────────────────────────────────────────────

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text(f"❌ No access  |  ID: `{user_id}`", parse_mode="Markdown")
        return

    cpu    = psutil.cpu_percent(interval=0.5)
    cores  = psutil.cpu_count()
    ram    = psutil.virtual_memory()
    disk   = psutil.disk_usage("/")
    uptime = os.popen("uptime -p").read().strip()

    msg = (
        f"📊 *Server Status*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_icon(cpu)}  *CPU*  —  `{cpu:.1f}%`  ({cores} cores)\n"
        f"`{bar(cpu)}`\n\n"
        f"{status_icon(ram.percent)}  *RAM*  —  `{ram.percent:.1f}%`\n"
        f"`{bar(ram.percent)}`  `{fmt_bytes(ram.used)} / {fmt_bytes(ram.total)}`\n\n"
        f"{status_icon(disk.percent)}  *Disk*  —  `{disk.percent:.1f}%`\n"
        f"`{bar(disk.percent)}`  `{fmt_bytes(disk.used)} / {fmt_bytes(disk.total)}`\n\n"
        f"⏱ *Uptime:* {uptime}"
    )
    logging.info(f"{user_id} used /status")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ──────────────────────────────────────────────
#  SYSTEM
# ──────────────────────────────────────────────

async def system(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access", parse_mode="Markdown")
        return

    total_ram = psutil.virtual_memory().total
    processes = sorted(
        psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'memory_info']),
        key=lambda p: p.info['cpu_percent'],
        reverse=True
    )[:5]

    msg = "🔥 *Top CPU Processes*\n━━━━━━━━━━━━━━━━━━━━\n"
    for i, p in enumerate(processes, 1):
        cpu_p  = p.info['cpu_percent']
        ram_p  = p.info['memory_percent'] or 0
        ram_mb = fmt_bytes(p.info['memory_info'].rss) if p.info['memory_info'] else "?"
        msg += (
            f"`{i}.` *{p.info['name'][:20]}*\n"
            f"   CPU: `{cpu_p:.1f}%`  "
            f"RAM: `{ram_p:.1f}%` (`{ram_mb}`)\n"
        )

    logging.info(f"{user_id} used /system")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ──────────────────────────────────────────────
#  NETWORK
# ──────────────────────────────────────────────

async def network(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    net   = psutil.net_io_counters()
    conns = len(psutil.net_connections())

    msg = (
        f"🌐 *Network*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 *Sent:*  `{fmt_bytes(net.bytes_sent)}`  ({net.packets_sent:,} packets)\n"
        f"📥 *Recv:*  `{fmt_bytes(net.bytes_recv)}`  ({net.packets_recv:,} packets)\n"
        f"🔗 *Active connections:* `{conns}`"
    )
    logging.info(f"{user_id} used /network")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ──────────────────────────────────────────────
#  STORAGE
# ──────────────────────────────────────────────

async def storage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    disk = psutil.disk_usage("/")

    msg = (
        f"💾 *Storage*\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"{status_icon(disk.percent)} `{bar(disk.percent)}`  `{disk.percent:.1f}%`\n"
        f"`{fmt_bytes(disk.used)} / {fmt_bytes(disk.total)}`\n\n"
        f"📦 *Total:* `{fmt_bytes(disk.total)}`\n"
        f"🔴 *Used:*  `{fmt_bytes(disk.used)}`\n"
        f"🟢 *Free:*  `{fmt_bytes(disk.free)}`"
    )
    logging.info(f"{user_id} used /storage")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ──────────────────────────────────────────────
#  SERVICES
# ──────────────────────────────────────────────

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        await update.message.reply_text("❌ No access")
        return

    svcs = ["ssh", "nginx", "docker"]
    msg  = "🛠 *Services Status*\n━━━━━━━━━━━━━━━━━━━━\n"
    for s in svcs:
        st   = os.popen(f"systemctl is-active {s}").read().strip()
        icon = "✅" if st == "active" else "❌"
        msg += f"{icon}  `{s:<10}` — {st}\n"

    logging.info(f"{user_id} used /services")
    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ──────────────────────────────────────────────
#  REBOOT / SHUTDOWN
# ──────────────────────────────────────────────

async def reboot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only  |  ID: `{user_id}`", parse_mode="Markdown")
        return
    await update.message.reply_text("🔄 *Rebooting server…*", parse_mode="Markdown")
    os.system("sudo reboot")


async def shutdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only  |  ID: `{user_id}`", parse_mode="Markdown")
        return
    await update.message.reply_text("🛑 *Shutting down server…*", parse_mode="Markdown")
    os.system("sudo shutdown now")


# ──────────────────────────────────────────────
#  LOG
# ──────────────────────────────────────────────

async def get_logs(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only  |  ID: `{user_id}`", parse_mode="Markdown")
        return

    try:
        with open(LOG_FILE, "r") as f:
            lines = f.readlines()[-20:]
        if not lines:
            await update.message.reply_text("📭 No logs yet.")
            return
        content = "".join(lines)
        msg = f"📜 *Last 20 log lines*\n━━━━━━━━━━━━━━━━━━━━\n```\n{content}```"
        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())
        logging.info(f"Admin {user_id} requested /log")
    except FileNotFoundError:
        await update.message.reply_text(f"❌ Log file `{LOG_FILE}` not found.", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")


# ──────────────────────────────────────────────
#  LIST USERS
# ──────────────────────────────────────────────

async def list_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        await update.message.reply_text(f"❌ Admin only  |  ID: `{user_id}`", parse_mode="Markdown")
        return

    if not users_db:
        await update.message.reply_text("📭 No users registered yet.")
        return

    msg = "👥 *Registered Users*\n━━━━━━━━━━━━━━━━━━━━\n"
    for uid, name in users_db.items():
        role = "👑" if is_admin(uid) else "👤"
        msg += f"{role} *{name}*\n   ID: `{uid}`\n"

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())


# ──────────────────────────────────────────────
#  CALLBACK HANDLER (inline buttons)
# ──────────────────────────────────────────────

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query    = update.callback_query
    user_id  = query.from_user.id
    data     = query.data
    await query.answer()

    # Proxy to the right function using a fake Update-like object
    # We reuse existing functions but reply via edit_message_text

    async def reply(text, **kwargs):
        await query.edit_message_text(text, **kwargs)

    # Swap the reply method temporarily via context
    context.user_data["_edit"] = query

    if data == "menu":
        name = users_db.get(user_id, "User")
        role = "👑 Admin" if is_admin(user_id) else "👤 User"
        msg  = (
            f"🤖 *Server Monitor Bot*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"Hello, *{name}*!  {role}\n\n"
            f"Choose an action from the menu below 👇"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=main_menu_keyboard(user_id))
        return

    if data == "ping":
        await query.edit_message_text("🏓 *Pong!* Bot is alive.", parse_mode="Markdown", reply_markup=back_keyboard())
        return

    if data == "status":
        if not is_authorized(user_id):
            await query.edit_message_text("❌ No access")
            return
        cpu    = psutil.cpu_percent(interval=0.5)
        cores  = psutil.cpu_count()
        ram    = psutil.virtual_memory()
        disk   = psutil.disk_usage("/")
        uptime = os.popen("uptime -p").read().strip()
        msg = (
            f"📊 *Server Status*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{status_icon(cpu)}  *CPU*  —  `{cpu:.1f}%`  ({cores} cores)\n"
            f"`{bar(cpu)}`\n\n"
            f"{status_icon(ram.percent)}  *RAM*  —  `{ram.percent:.1f}%`\n"
            f"`{bar(ram.percent)}`  `{fmt_bytes(ram.used)} / {fmt_bytes(ram.total)}`\n\n"
            f"{status_icon(disk.percent)}  *Disk*  —  `{disk.percent:.1f}%`\n"
            f"`{bar(disk.percent)}`  `{fmt_bytes(disk.used)} / {fmt_bytes(disk.total)}`\n\n"
            f"⏱ *Uptime:* {uptime}"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "system":
        if not is_authorized(user_id):
            await query.edit_message_text("❌ No access")
            return
        processes = sorted(
            psutil.process_iter(['name', 'cpu_percent', 'memory_percent', 'memory_info']),
            key=lambda p: p.info['cpu_percent'], reverse=True
        )[:5]
        msg = "🔥 *Top CPU Processes*\n━━━━━━━━━━━━━━━━━━━━\n"
        for i, p in enumerate(processes, 1):
            cpu_p  = p.info['cpu_percent']
            ram_p  = p.info['memory_percent'] or 0
            ram_mb = fmt_bytes(p.info['memory_info'].rss) if p.info['memory_info'] else "?"
            msg += (
                f"`{i}.` *{p.info['name'][:20]}*\n"
                f"   CPU: `{cpu_p:.1f}%`  "
                f"RAM: `{ram_p:.1f}%` (`{ram_mb}`)\n"
            )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "network":
        if not is_authorized(user_id):
            await query.edit_message_text("❌ No access")
            return
        net   = psutil.net_io_counters()
        conns = len(psutil.net_connections())
        msg = (
            f"🌐 *Network*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"📤 *Sent:*  `{fmt_bytes(net.bytes_sent)}`  ({net.packets_sent:,} packets)\n"
            f"📥 *Recv:*  `{fmt_bytes(net.bytes_recv)}`  ({net.packets_recv:,} packets)\n"
            f"🔗 *Active connections:* `{conns}`"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "storage":
        if not is_authorized(user_id):
            await query.edit_message_text("❌ No access")
            return
        disk = psutil.disk_usage("/")
        msg = (
            f"💾 *Storage*\n"
            f"━━━━━━━━━━━━━━━━━━━━\n"
            f"{status_icon(disk.percent)} `{bar(disk.percent)}`  `{disk.percent:.1f}%`\n"
            f"`{fmt_bytes(disk.used)} / {fmt_bytes(disk.total)}`\n\n"
            f"📦 *Total:* `{fmt_bytes(disk.total)}`\n"
            f"🔴 *Used:*  `{fmt_bytes(disk.used)}`\n"
            f"🟢 *Free:*  `{fmt_bytes(disk.free)}`"
        )
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "services":
        if not is_authorized(user_id):
            await query.edit_message_text("❌ No access")
            return
        svcs = ["ssh", "nginx", "docker"]
        msg  = "🛠 *Services Status*\n━━━━━━━━━━━━━━━━━━━━\n"
        for s in svcs:
            st   = os.popen(f"systemctl is-active {s}").read().strip()
            icon = "✅" if st == "active" else "❌"
            msg += f"{icon}  `{s:<10}` — {st}\n"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "log":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Admin only")
            return
        try:
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()[-20:]
            content = "".join(lines) if lines else "No logs yet."
            msg = f"📜 *Last 20 log lines*\n━━━━━━━━━━━━━━━━━━━━\n```\n{content}```"
            await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {e}")

    elif data == "list":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Admin only")
            return
        if not users_db:
            await query.edit_message_text("📭 No users registered yet.", reply_markup=back_keyboard())
            return
        msg = "👥 *Registered Users*\n━━━━━━━━━━━━━━━━━━━━\n"
        for uid, name in users_db.items():
            role = "👑" if is_admin(uid) else "👤"
            msg += f"{role} *{name}*\n   ID: `{uid}`\n"
        await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=back_keyboard())

    elif data == "reboot":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Admin only")
            return
        await query.edit_message_text("🔄 *Rebooting server…*", parse_mode="Markdown")
        os.system("sudo reboot")

    elif data == "shutdown":
        if not is_admin(user_id):
            await query.edit_message_text("❌ Admin only")
            return
        await query.edit_message_text("🛑 *Shutting down server…*", parse_mode="Markdown")
        os.system("sudo shutdown now")