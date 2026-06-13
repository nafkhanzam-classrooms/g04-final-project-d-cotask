import socket
import threading
import json
import time
import hashlib

from protocol import *
from server_state import *


HOST = "127.0.0.1"
PORT = 5000


USER_FILE = "users.json"


def load_users():

    try:

        with open(
            USER_FILE,
            "r"
        ) as file:

            return json.load(file)

    except:

        return {}
    
def save_users(users):

    with open(
        USER_FILE,
        "w"
    ) as file:

        json.dump(
            users,
            file,
            indent=4
        )

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

STATE_FILE = "state.json"

def save_state():
    state = {
        "rooms": rooms,
        "tasks": tasks,
        "chat_history": chat_history,
        "private_messages": private_messages,
    }
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
    except Exception as e:
        print(f"[WARN] Gagal simpan state: {e}")

def load_state():
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        rooms.update(state.get("rooms", {}))
        tasks.update(state.get("tasks", {}))
        chat_history.update(state.get("chat_history", {}))
        private_messages.update(state.get("private_messages", {}))
        print("[INFO] State berhasil dimuat.")
    except FileNotFoundError:
        print("[INFO] Tidak ada state tersimpan, mulai fresh.")
    except Exception as e:
        print(f"[WARN] Gagal load state: {e}")

def handle_register(
    packet,
    client_socket
):

    username = packet["sender"]

    password = packet[
        "data"
    ]["password"]

    users = load_users()

    if username in users:

        response = packet_error(
            "Username already exists"
        )

    else:

        users[username] = {
            "password": hash_password(password)
        }

        save_users(users)

        response = packet_success(
            "Register successful"
        )

        print(
            f"[REGISTER] {username}"
        )

    client_socket.send(
        serialize(response).encode()
    )

# ==========================================
# LOGIN HANDLER
# ==========================================

def handle_login(
    packet,
    client_socket
):

    username = packet["sender"]

    password = packet[
        "data"
    ]["password"]

    users = load_users()

    if username not in users:

        response = packet_error(
            "User not registered"
        )

    elif users[
        username
    ]["password"] != hash_password(password):

        response = packet_error(
            "Wrong password"
        )

    elif username in online_users:

        response = packet_error(
            "User already online"
        )

    else:

        online_users[
            username
        ] = client_socket

        response = packet_success(
            "Login successful"
        )

        print(
            f"[LOGIN] {username}"
        )

        print(
            f"ONLINE USERS: "
            f"{list(online_users.keys())}"
        )

    client_socket.send(
        serialize(response).encode()
    )


# ==========================================
# REMOVE USER
# ==========================================

def remove_user(client_socket):

    disconnected_user = None

    for username, sock in online_users.items():

        if sock == client_socket:

            disconnected_user = username
            break

    if disconnected_user:

        del online_users[
            disconnected_user
        ]

        # HAPUS DARI ROOM
        for room_name in rooms:

            members = rooms[
                room_name
            ]["members"]

            if disconnected_user in members:

                members.remove(
                    disconnected_user
                )

                print(
                    f"[AUTO LEAVE] "
                    f"{disconnected_user} "
                    f"removed from "
                    f"{room_name}"
                )

        # HAPUS DARI ROOM_SOCKETS
        for room_name in room_sockets:
            room_sockets[room_name] = [
                (u, s) for u, s in room_sockets[room_name]
                if u != disconnected_user
            ]

        # HAPUS DARI USER_CURRENT_ROOM
        if disconnected_user in user_current_room:
            del user_current_room[disconnected_user]

        print(
            f"[DISCONNECTED] "
            f"{disconnected_user}"
        )

        print(
            f"ONLINE USERS: "
            f"{list(online_users.keys())}"
        )

        print("\nROOMS:")
        print(rooms)

# ==========================================
# BROADCAST TO ROOM
# ==========================================

def broadcast_to_room(
    room_name,
    packet
):
    """Send packet to all active clients in a room"""

    if room_name not in room_sockets:
        return

    disconnected = []

    for username, sock in room_sockets[
        room_name
    ]:
        try:
            sock.send(
                serialize(packet).encode()
            )
        except Exception as e:
            print(
                f"[BROADCAST ERROR] "
                f"Failed to send to {username}: {e}"
            )
            disconnected.append(
                (username, sock)
            )

    for item in disconnected:
        room_sockets[
            room_name
        ].remove(item)

# ==========================================
# SEND PM NOTIFICATION
# ==========================================

def send_pm_notification(
    recipient,
    sender
):
    """Notify user of incoming PM"""

    if recipient not in online_users:
        return

    packet = create_packet(
        TASK_NOTIFICATION,
        data={
            "message": f"New message from {sender}"
        }
    )

    try:
        online_users[
            recipient
        ].send(
            serialize(packet).encode()
        )
    except:
        pass

# ==========================================
# CLIENT THREAD
# ==========================================

def handle_client(
    client_socket,
    address
):

    print(
        f"[CONNECTED] {address}"
    )

    client_socket.settimeout(None)

    while True:

        try:

            data = client_socket.recv(
                4096
            )

            if not data:
                break

            last_activity = time.time()
            message = data.decode()

            packet = deserialize(
                message
            )

            packet_type = packet["type"]

            # ==========================
            # PING
            # ==========================

            if packet_type == PING:
                response = create_packet(
                    PONG
                )
                client_socket.send(
                    serialize(
                        response
                    ).encode()
                )
                continue

            # ==========================
            # LOGIN
            # ==========================

            if packet_type == LOGIN:

                handle_login(
                    packet,
                    client_socket
                )
            
            elif packet_type == REGISTER:

                handle_register(
                    packet,
                    client_socket
                )
            
            elif packet_type == CREATE_ROOM:

                handle_create_room(
                    packet,
                    client_socket
                )

            elif packet_type == JOIN_ROOM:

                handle_join_room(
                    packet,
                    client_socket
                )

            elif packet_type == ENTER_ROOM:

                handle_enter_room(
                    packet,
                    client_socket
                )

            elif packet_type == ROOM_LIST:

                handle_room_list(
                    client_socket
                )

            elif packet_type == LEAVE_ROOM:

                handle_leave_room(
                    packet,
                    client_socket
                )

            elif packet_type == BROADCAST:

                handle_broadcast(
                    packet,
                    client_socket
                )

            elif packet_type == PRIVATE_MESSAGE:

                handle_private_message(
                    packet,
                    client_socket
                )

            elif packet_type == GET_PRIVATE_MESSAGES:

                handle_get_private_messages(
                    packet,
                    client_socket
                )

            elif packet_type == ONLINE_USERS:

                handle_online_users(
                    client_socket
                )

            elif packet_type == GET_HISTORY:

                handle_get_history(
                    packet,
                    client_socket
                )

            elif packet_type == CREATE_TASK:

                handle_create_task(
                    packet,
                    client_socket
                )

            elif packet_type == TASK_BOARD:

                handle_task_board(
                    packet,
                    client_socket
                )

            elif packet_type == ASSIGN_TASK:

                handle_assign_task(
                    packet,
                    client_socket
                )

            elif packet_type == UPDATE_TASK:

                handle_update_task(
                    packet,
                    client_socket
                )

            elif packet_type == DELETE_TASK:

                handle_delete_task(
                    packet,
                    client_socket
                )

            else:

                response = packet_error(
                    "Unknown packet type"
                )

                client_socket.send(
                    serialize(
                        response
                    ).encode()
                )

        except socket.timeout:
            # Client idle, lanjutkan — jangan disconnect
            continue

        except Exception as e:

            print(
                f"[ERROR] {e}"
            )

            break

    remove_user(client_socket)

    client_socket.close()

    print(
        f"[THREAD CLOSED] {address}"
    )

    print(
        f"[ACTIVE THREADS] "
        f"{threading.active_count()-2}"
    )
    
# ==========================================
# START SERVER
# ==========================================

def start_server():

    server = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # ← tambah ini

    server.bind(
        (HOST, PORT)
    )

    server.listen()

    print(
        "\n=== COTASK SERVER ==="
    )

    print(
        f"Listening on {HOST}:{PORT}"
    )

    while True:

        client_socket, address = (
            server.accept()
        )

        thread = threading.Thread(
            target=handle_client,
            args=(
                client_socket,
                address
            )
        )

        thread.daemon = True

        thread.start()

        print(
            f"[ACTIVE THREADS] "
            f"{threading.active_count()-1}"
        )

# CREATE ROOM
def handle_create_room(
    packet,
    client_socket
):
    room_name = packet["room"]

    if room_name in rooms:

        response = packet_error(
            "Room already exists"
        )

    else:

        rooms[room_name] = {
            "members": [
                packet["sender"]
            ]
        }
        save_state()

        response = packet_success(
            f"Room {room_name} created"
        )

        print(
            f"[ROOM CREATED] "
            f"{room_name}"
        )

        print("\nROOMS:")
        print(rooms)

    client_socket.send(
        serialize(response).encode()
    )

# JOIN ROOM
def handle_join_room(
    packet,
    client_socket
):

    username = packet["sender"]
    room_name = packet["room"]

    if room_name not in rooms:

        response = packet_error(
            "Room not found"
        )

    else:

        if username not in rooms[
            room_name
        ]["members"]:

            rooms[room_name][
                "members"
            ].append(username)

        if room_name not in room_sockets:
            room_sockets[room_name] = []

        if (username, client_socket) not in room_sockets[room_name]:
            room_sockets[room_name].append(
                (username, client_socket)
            )

        user_current_room[username] = room_name
        save_state()

        response = packet_success(
            f"Joined {room_name}"
        )

        print(
            f"[JOIN ROOM] "
            f"{username} -> {room_name}"
        )

    print("\nROOMS:")
    print(rooms)

    client_socket.send(
        serialize(response).encode()
    )

# ENTER ROOM
def handle_enter_room(
    packet,
    client_socket
):

    username = packet["sender"]

    room_name = packet["room"]

    if room_name not in rooms:

        response = packet_error(
            "Room not found"
        )

    elif username not in rooms[
        room_name
    ]["members"]:

        response = packet_error(
            "You are not a member of this room"
        )

    else:

        if room_name not in room_sockets:
            room_sockets[room_name] = []

        if (username, client_socket) not in room_sockets[room_name]:
            room_sockets[room_name].append(
                (username, client_socket)
            )

        user_current_room[username] = room_name
        save_state()

        response = packet_success(
            f"Entered {room_name}"
        )

        print(
            f"[ENTER ROOM] "
            f"{username} -> {room_name}"
        )

    client_socket.send(
        serialize(response).encode()
    )

# ROOM LIST
def handle_room_list(
    client_socket
):

    response = create_packet(
        ROOM_LIST,
        data={
            "rooms":
            list(rooms.keys())
        }
    )

    client_socket.send(
        serialize(response).encode()
    )

# BROADCAST MESSAGE
def handle_broadcast(
    packet,
    client_socket
):

    username = packet["sender"]
    room_name = packet["room"]
    message = packet["data"]["message"]

    if room_name not in rooms:

        response = packet_error(
            "Room not found"
        )

        client_socket.send(
            serialize(
                response
            ).encode()
        )

        return

    if room_name not in chat_history:

        chat_history[
            room_name
        ] = []

    chat_history[
        room_name
    ].append({

        "sender": username,

        "message": message,

        "timestamp": packet[
            "timestamp"
        ]
    })
    save_state()

    print(
        f"[BROADCAST SAVED] "
        f"{username} -> {room_name}"
    )

    response = packet_success(
        "Broadcast saved"
    )

    client_socket.send(
        serialize(
            response
        ).encode()
    )

    # PUSH TO ALL ACTIVE CLIENTS IN ROOM
    broadcast_packet = create_packet(
        BROADCAST,
        sender=username,
        room=room_name,
        data={
            "message": message
        }
    )

    broadcast_to_room(
        room_name,
        broadcast_packet
    )

#PRIVATE MESSAGE
def handle_private_message(
    packet,
    client_socket
):

    sender = packet["sender"]

    target = packet["data"]["target"]

    message = packet["data"]["message"]

    if target not in online_users and target not in load_users():

        response = packet_error(
            "Target user not found"
        )

    else:

        if sender not in private_messages:
            private_messages[sender] = {}

        if target not in private_messages[sender]:
            private_messages[sender][target] = []

        private_messages[sender][target].append({
            "message": message,
            "timestamp": packet["timestamp"],
            "read": False
        })

        print(
            f"[PM] {sender} -> {target}"
        )

        response = packet_success(
            "Private message saved"
        )

        send_pm_notification(target, sender)

    client_socket.send(
        serialize(
            response
        ).encode()
    )

# GET PRIVATE MESSAGES
def handle_get_private_messages(
    packet,
    client_socket
):

    username = packet["sender"]

    user_pms = {}

    for sender in private_messages:
        if username in private_messages[sender]:
            user_pms[sender] = private_messages[sender][username]

    response = create_packet(
        GET_PRIVATE_MESSAGES,
        sender=username,
        data={
            "messages": user_pms
        }
    )

    print(
        f"[GET PM] {username}"
    )

    client_socket.send(
        serialize(response).encode()
    )

# ONLINE USERS
def handle_online_users(
    client_socket
):

    response = create_packet(
        ONLINE_USERS,
        data={
            "users":
            list(
                online_users.keys()
            )
        }
    )

    client_socket.send(
        serialize(
            response
        ).encode()
    )

def handle_get_history(
    packet,
    client_socket
):

    room_name = packet["room"]

    history = chat_history.get(
        room_name,
        []
    )

    response = create_packet(
        GET_HISTORY,
        room=room_name,
        data={
            "history": history
        }
    )

    print("\n=== HISTORY RESPONSE ===")
    print(response)

    client_socket.send(
        serialize(
            response
        ).encode()
    )

    print(
        f"[GET HISTORY] "
        f"{room_name}"
    )
    

# LEAVE ROOM
def handle_leave_room(
    packet,
    client_socket
):

    username = packet["sender"]
    room_name = packet["room"]

    if room_name not in rooms:

        response = packet_error(
            "Room not found"
        )

    else:

        members = rooms[
            room_name
        ]["members"]

        if username not in members:

            response = packet_error(
                "You are not in this room"
            )

        else:

            members.remove(
                username
            )

            if room_name in room_sockets:
                room_sockets[room_name] = [
                    (u, s) for u, s in room_sockets[room_name]
                    if u != username
                ]

            if username in user_current_room:
                if user_current_room[username] == room_name:
                    del user_current_room[username]

            response = packet_success(
                f"Left {room_name}"
            )

            print(
                f"[LEAVE ROOM] "
                f"{username} -> {room_name}"
            )

            print("\nROOMS:")
            print(rooms)

    client_socket.send(
        serialize(response).encode()
    )

# MASUK KE FITUR TAMBAHAN (TASK BOARD)  
def handle_create_task(
    packet,
    client_socket
):

    room_name = packet["room"]

    username = packet["sender"]

    title = packet[
        "data"
    ]["title"]

    if room_name not in rooms:

        response = packet_error(
            "Room not found"
        )

    elif username not in rooms[
        room_name
    ]["members"]:

        response = packet_error(
            "You are not a member"
        )

    else:

        if room_name not in tasks:

            tasks[room_name] = []

        task_id = len(
            tasks[room_name]
        ) + 1

        task = {

            "id": task_id,

            "title": title,

            "assignee": "",

            "status": "TODO",

            "created_by": username

        }

        tasks[
            room_name
        ].append(task)
        save_state()

        print(
            f"[TASK CREATED] "
            f"{title}"
        )

        response = packet_success(
            "Task created"
        )

    client_socket.send(
        serialize(response).encode()
    )

def handle_task_board(
    packet,
    client_socket
):

    room_name = packet["room"]

    room_tasks = tasks.get(
        room_name,
        []
    )

    response = create_packet(

        TASK_BOARD,

        room=room_name,

        data={

            "tasks": room_tasks

        }
    )

    client_socket.send(
        serialize(response).encode()
    )

def handle_assign_task(
    packet,
    client_socket
):

    room_name = packet["room"]

    task_id = packet["data"]["task_id"]

    assignee = packet["data"]["assignee"]

    if room_name not in rooms:

        response = packet_error(
            "Room not found"
        )

    elif assignee not in rooms[
        room_name
    ]["members"]:

        response = packet_error(
            "User is not a room member"
        )

    else:

        found = False

        for task in tasks.get(
            room_name,
            []
        ):

            if task["id"] == task_id:

                task[
                    "assignee"
                ] = assignee

                send_task_notification(

                    assignee,

                    f"You have been assigned task: "
                    f"{task['title']}"

                )

                found = True

                break

        if found:

            response = packet_success(
                "Task assigned"
            )

        else:

            response = packet_error(
                "Task not found"
            )

    client_socket.send(
        serialize(response).encode()
    )

def handle_update_task(
    packet,
    client_socket
):

    room_name = packet["room"]

    username = packet["sender"]

    task_id = packet["data"]["task_id"]

    new_status = packet["data"]["status"]

    valid_status = [
        "TODO",
        "IN_PROGRESS",
        "DONE"
    ]

    if new_status not in valid_status:

        response = packet_error(
            "Invalid status"
        )

    else:

        task_found = False

        for task in tasks.get(
            room_name,
            []
        ):

            if task["id"] == task_id:

                task_found = True

                if task[
                    "assignee"
                ] != username:

                    response = packet_error(
                        "Only assignee can update this task"
                    )

                else:

                    old_status = task[
                        "status"
                    ]

                    task[
                        "status"
                    ] = new_status

                    print(
                        f"[TASK UPDATED] "
                        f"{task['title']} "
                        f"{old_status} -> "
                        f"{new_status}"
                    )

                    response = packet_success(
                        "Task updated"
                    )

                    # =====================
                    # TASK COMPLETED
                    # NOTIFICATION
                    # =====================

                    if new_status == "DONE":

                        creator = task[
                            "created_by"
                        ]

                        send_task_notification(

                            creator,

                            f"Task completed: "
                            f"{task['title']}"

                        )

                break

        if not task_found:

            response = packet_error(
                "Task not found"
            )

    client_socket.send(
        serialize(response).encode()
    )


def handle_delete_task(
    packet,
    client_socket
):

    room_name = packet["room"]
    username = packet["sender"]
    task_id = packet["data"]["task_id"]

    if room_name not in rooms:
        response = packet_error("Room not found")
        client_socket.send(serialize(response).encode())
        return

    task_found = False

    for task in tasks.get(room_name, []):

        if task["id"] == task_id:
            task_found = True

            # Hanya creator atau assignee yang boleh hapus
            if username != task["created_by"] and username != task["assignee"]:
                response = packet_error(
                    "Only creator or assignee can delete this task"
                )
            else:
                tasks[room_name].remove(task)

                response = packet_success(
                    f"Task '{task['title']}' deleted"
                )

                print(f"[DELETE TASK] '{task['title']}' by {username}")

                # Notifikasi ke semua member room
                notif_msg = f"Task '{task['title']}' was deleted by {username}"
                for member in rooms[room_name]["members"]:
                    if member != username:
                        send_task_notification(member, notif_msg)
            break

    if not task_found:
        response = packet_error("Task not found")

    client_socket.send(serialize(response).encode())

def send_task_notification(
    username,
    message
):

    if username not in online_users:

        return

    packet = create_packet(

        TASK_NOTIFICATION,

        data={
            "message": message
        }

    )

    try:

        online_users[
            username
        ].send(

            serialize(
                packet
            ).encode()

        )

    except:

        pass

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    load_state()
    start_server()
