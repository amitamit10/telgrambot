# 🤖 Server Monitor Bot

A Telegram bot for real-time Linux server monitoring and management. Monitor CPU, RAM, disk, network, and services — all from your Telegram app.

---

## Features

- 📊 Live server stats (CPU, RAM, disk, uptime)
- 🌐 Network I/O monitoring
- 🔥 Top resource-consuming processes
- 🛠 Service status checks (SSH, Nginx, Docker)
- 💾 Disk usage breakdown
- 🔐 Role-based access control (Users & Admins)
- 🖥 Terminal control panel for live user management
- 📜 Log viewer via Telegram

---

## Project Structure

```
├── main.py        # Bot entry point & handler registration
├── commands.py    # All bot command logic
├── auth.py        # Authorization & admin check helpers
├── terminal.py    # Local terminal panel for managing users
├── config.py      # Bot token configuration
└── bot.log        # Runtime log file
```

---

## Requirements

- Python 3.10+
- [`python-telegram-bot`](https://github.com/python-telegram-bot/python-telegram-bot) v20+
- [`psutil`](https://github.com/giampaolo/psutil)

Install dependencies:

```bash
pip install python-telegram-bot psutil
```

---

## Setup

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd <repo-folder>
```

2. **Configure the bot token**

Open `config.py` and replace the placeholder with your bot token from [@BotFather](https://t.me/BotFather):

```python
BOT_TOKEN = "your-telegram-bot-token-here"
```

3. **Set your Telegram user ID**

Open `auth.py` and replace `123456789` with your actual Telegram user ID in both sets:

```python
AUTHORIZED_USERS = set([
    YOUR_TELEGRAM_ID,
])

ADMIN_USERS = set([
    YOUR_TELEGRAM_ID,
])
```

> 💡 You can find your Telegram ID by messaging [@userinfobot](https://t.me/userinfobot).

4. **Run the bot**

```bash
python main.py
```

---

## Bot Commands

### General Commands (All authorized users)

| Command | Description |
|---|---|
| `/start` | Show welcome message and command list |
| `/ping` | Check if the bot is alive |
| `/status` | CPU, RAM, disk usage & uptime |
| `/system` | Top 5 CPU-consuming processes |
| `/network` | Network bytes sent/received |
| `/storage` | Total, used, and free disk space |
| `/services` | Status of SSH, Nginx, and Docker |

### Admin Commands

| Command | Description |
|---|---|
| `/log` | View the last 20 lines of the bot log |
| `/list` | List all registered users |
| `/reboot` | Reboot the server |
| `/shutdown` | Shut down the server |

---

## Terminal Control Panel

When the bot is running, a local terminal panel is available for managing users in real time:

```
panel > add <user_id>       # Authorize a user
panel > addadmin <user_id>  # Add a user as admin (also authorizes them)
panel > remove <user_id>    # Remove user/admin access
panel > list                # Show all authorized users and admins
panel > clear               # Clear the terminal screen
panel > exit                # Close the panel
```

---

## User Registration Flow

New users are prompted to enter their name when they first message the bot. Once registered, they can use commands if their ID has been added to the authorized list via the terminal panel or `auth.py`.

---

## Security Notes

- Only users listed in `AUTHORIZED_USERS` can run monitoring commands.
- Only users in `ADMIN_USERS` can run destructive commands (`/reboot`, `/shutdown`).
- The terminal panel runs locally on the server — it is not accessible via Telegram.
- **Never commit your bot token to version control.** Consider using environment variables:

```python
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN")
```

---

## License

MIT — feel free to use, modify, and distribute.