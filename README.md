# 🤖 Server Monitor Bot

A Telegram bot for real-time Linux server monitoring, management, and file transfers — all from your Telegram app.

---

## Features

- 📊 Live server stats (CPU, RAM, disk, uptime)
- 🌐 Network I/O monitoring
- 🔥 Top resource-consuming processes
- 🛠 Service status checks (SSH, Nginx, Docker)
- 💾 Disk usage breakdown
- 📁 File transfer support
- 🔐 Role-based access control (Users & Admins)
- 🖥 Terminal control panel for live user management
- 📜 Log viewer via Telegram
- 🎛 Inline button menu for easy navigation

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
git clone https://github.com/amitamit10/telgrambot.git
cd telgrambot
```

2. **Configure the bot token**

Open `config.py` and replace the placeholder with your bot token from [@BotFather](https://t.me/BotFather):

```python
BOT_TOKEN = "your-telegram-bot-token-here"
```



4. **Run the bot**

```bash
python main.py
```

---

## Bot Commands

### General (All authorized users)

| Command | Description |
|---|---|
| `/start` | Show welcome message & inline menu |
| `/ping` | Check if the bot is alive |
| `/status` | CPU, RAM, disk usage & uptime |
| `/system` | Top 5 CPU-consuming processes |
| `/network` | Network bytes sent/received |
| `/storage` | Total, used, and free disk space |
| `/services` | Status of SSH, Nginx, and Docker |

### Admin Only

| Command | Description |
|---|---|
| `/log` | View the last 20 lines of the bot log |
| `/list` | List all registered users |
| `/reboot` | Reboot the server |
| `/shutdown` | Shut down the server |

---

## Terminal Control Panel

A local terminal panel runs alongside the bot for real-time user management:

```
panel > add <user_id>       # Authorize a user
panel > addadmin <user_id>  # Add a user as admin (also authorizes them)
panel > remove <user_id>    # Remove user/admin access
panel > list                # Show all authorized users and admins
panel > clear               # Clear the terminal screen
panel > help                # Show available commands
panel > exit                # Close the panel
```

---

## User Registration Flow

When a new user messages the bot for the first time, they are prompted to enter their name. Once registered, they can use commands if their ID has been added to the authorized list via the terminal panel or `auth.py`.

---

## Security Notes

- Only users in `AUTHORIZED_USERS` can run monitoring commands.
- Only users in `ADMIN_USERS` can run destructive commands (`/reboot`, `/shutdown`).
- The terminal panel runs **locally on the server only** — not accessible via Telegram.
```
bot.log
config.py
```