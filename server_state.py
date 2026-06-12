# User online

online_users = {}

# Room

rooms = {}

# User aktif di room mana

user_rooms = {}

# Task per room

tasks = {}

# History chat

chat_history = {}

# private messages: {sender: {recipient: [{"message": str, "timestamp": str, "read": bool}]}}
private_messages = {}

# Active sockets per room: {room_name: [(username, socket), ...]}
room_sockets = {}

# Current active room for each user
user_current_room = {}