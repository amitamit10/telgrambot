import os
from auth import AUTHORIZED_USERS, ADMIN_USERS

# ─── ANSI Colors ───────────────────────────────
R  = "\033[0m"       # Reset
B  = "\033[1m"       # Bold
CY = "\033[96m"      # Cyan
GR = "\033[92m"      # Green
YE = "\033[93m"      # Yellow
RE = "\033[91m"      # Red
GY = "\033[90m"      # Gray
MA = "\033[95m"      # Magenta

def clear():
    os.system("clear")

def header():
    clear()
    print(f"{CY}{B}")
    print("  ╔══════════════════════════════════════╗")
    print("  ║         🖥  SERVER BOT  PANEL         ║")
    print("  ╚══════════════════════════════════════╝")
    print(f"{R}")

def help_table():
    print(f"{GY}  ┌─────────────────────────────────────────────┐{R}")
    print(f"{GY}  │{R}  {B}Command{R}               {B}Description{R}           {GY}│{R}")
    print(f"{GY}  ├─────────────────────────────────────────────┤{R}")
    cmds = [
        ("add <id>",      "Authorize a user"),
        ("addadmin <id>", "Add a user as admin"),
        ("remove <id>",   "Remove user / admin"),
        ("list",          "Show all users"),
        ("clear",         "Clear the screen"),
        ("help",          "Show this help"),
        ("exit",          "Close the panel"),
    ]
    for cmd, desc in cmds:
        print(f"{GY}  │{R}  {YE}{cmd:<22}{R}{desc:<23}{GY}│{R}")
    print(f"{GY}  └─────────────────────────────────────────────┘{R}")
    print()


def ok(msg):   print(f"  {GR}✔  {msg}{R}")
def err(msg):  print(f"  {RE}✘  {msg}{R}")
def info(msg): print(f"  {CY}ℹ  {msg}{R}")


def terminal_listener():
    header()
    help_table()

    while True:
        try:
            cmd = input(f"{MA}{B}  panel ›{R} ").strip()
        except (EOFError, KeyboardInterrupt):
            info("Closing panel…")
            break

        if not cmd:
            continue

        # ── add ──────────────────────────────────
        if cmd.startswith("add "):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isdigit():
                err("Usage:  add <user_id>")
                continue
            uid = int(parts[1])
            if uid in AUTHORIZED_USERS:
                info(f"{uid} is already authorized.")
            else:
                AUTHORIZED_USERS.add(uid)
                ok(f"User {CY}{uid}{R}{GR} added to authorized users.")

        # ── addadmin ─────────────────────────────
        elif cmd.startswith("addadmin "):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isdigit():
                err("Usage:  addadmin <user_id>")
                continue
            uid = int(parts[1])
            ADMIN_USERS.add(uid)
            AUTHORIZED_USERS.add(uid)
            ok(f"User {CY}{uid}{R}{GR} is now an admin 👑")

        # ── remove ───────────────────────────────
        elif cmd.startswith("remove "):
            parts = cmd.split()
            if len(parts) != 2 or not parts[1].isdigit():
                err("Usage:  remove <user_id>")
                continue
            uid = int(parts[1])
            if uid not in AUTHORIZED_USERS and uid not in ADMIN_USERS:
                err(f"User {uid} not found.")
            else:
                AUTHORIZED_USERS.discard(uid)
                ADMIN_USERS.discard(uid)
                ok(f"User {CY}{uid}{R}{GR} removed.")

        # ── list ─────────────────────────────────
        elif cmd == "list":
            print()
            print(f"{GY}  ┌──────────────────────────────────┐{R}")
            print(f"{GY}  │{R}  {B}{'ID':<15} {'Role':<10} {'Status'}{R}   {GY}│{R}")
            print(f"{GY}  ├──────────────────────────────────┤{R}")
            all_ids = AUTHORIZED_USERS | ADMIN_USERS
            if not all_ids:
                print(f"{GY}  │{R}    (no users)                  {GY}│{R}")
            for uid in sorted(all_ids):
                role   = f"{MA}Admin 👑{R}" if uid in ADMIN_USERS else f"{CY}User{R}"
                status = f"{GR}✔ authorized{R}"
                print(f"{GY}  │{R}  {uid:<15} {role:<10}  {status}  {GY}│{R}")
            print(f"{GY}  └──────────────────────────────────┘{R}")
            print()

        # ── clear ────────────────────────────────
        elif cmd == "clear":
            header()
            help_table()

        # ── help ─────────────────────────────────
        elif cmd == "help":
            help_table()

        # ── exit ─────────────────────────────────
        elif cmd == "exit":
            info("Closing panel…")
            break

        else:
            err(f"Unknown command: '{cmd}'  —  type {YE}help{R}{RE} for commands.")