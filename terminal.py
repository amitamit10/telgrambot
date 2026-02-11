from auth import AUTHORIZED_USERS

def terminal_listener():
    print("\n🖥 Terminal control ready")
    print("Commands:")
    print("  add <user_id>")
    print("  remove <user_id>")
    print("  list\n")

    while True:
        cmd = input(">> ")

        if cmd.startswith("add "):
            try:
                user_id = int(cmd.split()[1])
                AUTHORIZED_USERS.add(user_id)
                print(f"✅ Added {user_id}")
            except:
                print("❌ Use: add <user_id>")

        elif cmd.startswith("remove "):
            try:
                user_id = int(cmd.split()[1])
                AUTHORIZED_USERS.remove(user_id)
                print(f"🗑 Removed {user_id}")
            except:
                print("❌ User not found")

        elif cmd == "list":
            print("Authorized users:", AUTHORIZED_USERS)

        else:
            print("Unknown command")
