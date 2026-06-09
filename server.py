import socket
import threading

from protocol import *
from server_state import *


HOST = "127.0.0.1"
PORT = 5000


# ==========================================
# LOGIN HANDLER
# ==========================================

def handle_login(packet, client_socket):

    username = packet["sender"]

    if username in online_users:

        response = packet_error(
            "Username already in use"
        )

    else:

        online_users[username] = client_socket

        response = packet_success(
            "Login successful"
        )

        print(f"[LOGIN] {username}")

        print(
            f"ONLINE USERS: {list(online_users.keys())}"
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
# CLIENT THREAD
# ==========================================

def handle_client(
    client_socket,
    address
):

    print(
        f"[CONNECTED] {address}"
    )

    while True:

        try:

            data = client_socket.recv(
                4096
            )

            if not data:
                break

            message = data.decode()

            packet = deserialize(
                message
            )

            packet_type = packet["type"]

            # ==========================
            # LOGIN
            # ==========================

            if packet_type == LOGIN:

                handle_login(
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
                    packet
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


def handle_broadcast(
    packet
):

    sender = packet["sender"]

    room_name = packet["room"]

    message = packet[
        "data"
    ]["message"]

    if room_name not in rooms:

        return

    members = rooms[
        room_name
    ]["members"]

    broadcast_packet = create_packet(
        BROADCAST,
        sender=sender,
        room=room_name,
        data={
            "message": message
        }
    )

    serialized = serialize(
        broadcast_packet
    )

    print(
        f"[CHAT] "
        f"{sender}@{room_name}: "
        f"{message}"
    )

    for username in members:

        if username in online_users:

            try:

                online_users[
                    username
                ].send(
                    serialized.encode()
                )

            except:

                pass

def receive_messages(
    client
):

    while True:

        try:

            data = client.recv(
                4096
            ).decode()

            packet = deserialize(
                data
            )

            if packet["type"] == BROADCAST:

                print(
                    f"\n[{packet['room']}] "
                    f"{packet['sender']}: "
                    f"{packet['data']['message']}"
                )

        except:

            break

# ==========================================
# MAIN
# ==========================================

if __name__ == "__main__":

    start_server()