import os
from auth import AUTHORIZED_USERS, ADMIN_USERS

def terminal_listener():
    print("\n🖥 Terminal control ready")
    print("Commands:")
    print("  add <user_id>      -> Authorize user")
    print("  addadmin <user_id> -> Add admin")
    print("  remove <user_id>   -> Remove user/admin")
    print("  list               -> Show all users")
    print("  clear              -> Clear screen")
    print("  exit               -> Close panel\n")

    while True:
        cmd = input("panel > ").strip()

        if cmd.startswith("add "):
            try:
                user_id = int(cmd.split()[1])
                AUTHORIZED_USERS.add(user_id)
                print(f"✅ Added {user_id} to authorized users")
            except:
                print("❌ Use: add <user_id>")

        elif cmd.startswith("addadmin "):
            try:
                user_id = int(cmd.split()[1])
                ADMIN_USERS.add(user_id)
                AUTHORIZED_USERS.add(user_id)  # אדמין גם מורשה
                print(f"👑 Added {user_id} as admin")
            except:
                print("❌ Use: addadmin <user_id>")

        elif cmd.startswith("remove "):
            try:
                user_id = int(cmd.split()[1])
                AUTHORIZED_USERS.discard(user_id)
                ADMIN_USERS.discard(user_id)
                print(f"🗑 Removed {user_id}")
            except:
                print("❌ User not found")

        elif cmd == "list":
            print("Authorized users:", AUTHORIZED_USERS)
            print("Admin users:", ADMIN_USERS)

        elif cmd == "clear":
            os.system('clear')

        elif cmd == "exit":
            print("Exiting terminal panel...")
            break

        else:
            print("❌ Unknown command")
