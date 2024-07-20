def get_chat_name(message):
    chat = message.chat
    if chat.type == "private":
        return chat.username
    elif chat.type in ["group", "supergroup"]:
        return chat.title
