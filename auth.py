AUTHORIZED_USERS = set()

def is_authorized(chat_id: int):
    return chat_id in AUTHORIZED_USERS
