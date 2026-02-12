# רשימת משתמשים מורשים
AUTHORIZED_USERS = set([
    123456789,  # החלף ב-ID שלך
])

# רשימת אדמינים
ADMIN_USERS = set([
    123456789,  # החלף ב-ID שלך
])

def is_authorized(user_id: int) -> bool:
    return user_id in AUTHORIZED_USERS

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USERS
