import socket
from xmlrpc import client

from protocol import *

HOST = "127.0.0.1"
PORT = 5000


def send_packet(client, packet):

    client.send(
        serialize(packet).encode()
    )

    response = client.recv(
        4096
    ).decode()

    print("\nRAW RESPONSE:")
    print(response)

    return deserialize(response)


def main():

    username = input(
        "Username: "
    )

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect(
        (HOST, PORT)
    )

    # ==========================
    # LOGIN
    # ==========================

    login_packet = create_packet(
        LOGIN,
        sender=username
    )

    response = send_packet(
        client,
        login_packet
    )

    print("\nSERVER RESPONSE")
    print(response)

    # Jika login gagal
    if response["type"] == ERROR:

        print(
            "\nLogin gagal!"
        )

        client.close()

        return

    # ==========================
    # MAIN MENU
    # ==========================

    while True:

        print("\n===== MENU =====")
        print("1. Create Room")
        print("2. Join Room")
        print("3. Room List")
        print("4. Online Users")
        print("5. Broadcast Message")
        print("6. Private Message")
        print("7. Chat History")
        print("8. Leave Room")
        print("9. Exit")

        choice = input("> ")

        # ======================
        # CREATE ROOM
        # ======================

        if choice == "1":

            room_name = input(
                "Room Name: "
            )

            packet = create_packet(
                CREATE_ROOM,
                sender=username,
                room=room_name
            )

            response = send_packet(
                client,
                packet
            )

            print(
                "\nSERVER RESPONSE"
            )

            print(response)

        # ======================
        # JOIN ROOM
        # ======================

        elif choice == "2":

            room_name = input(
                "Room Name: "
            )

            packet = create_packet(
                JOIN_ROOM,
                sender=username,
                room=room_name
            )

            response = send_packet(
                client,
                packet
            )

            print(
                "\nSERVER RESPONSE"
            )

            print(response)

        # ======================
        # ROOM LIST
        # ======================

        elif choice == "3":

            packet = create_packet(
                ROOM_LIST,
                sender=username
            )

            response = send_packet(
                client,
                packet
            )

            rooms = response["data"]["rooms"]

            print("\n===== ROOM LIST =====")

            if not rooms:

                print("Belum ada room")

            else:

                for i, room in enumerate(
                    rooms,
                    start=1
                ):

                    print(
                        f"{i}. {room}"
                    )

        elif choice == "4":

            packet = create_packet(
                ONLINE_USERS,
                sender=username
            )

            response = send_packet(
                client,
                packet
            )

            users = response["data"]["users"]

            print(
                "\n===== ONLINE USERS ====="
            )

            for user in users:

                print(user)

        elif choice == "5":

            room_name = input(
                "Room Name: "
            )

            message = input(
                "Message: "
            )

            packet = create_packet(
                BROADCAST,
                sender=username,
                room=room_name,
                data={
                    "message": message
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

        elif choice == "6":

            target = input(
                "Target User: "
            )

            message = input(
                "Message: "
            )

            packet = create_packet(
                PRIVATE_MESSAGE,
                sender=username,
                data={
                    "target": target,
                    "message": message
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)


        elif choice == "7":

            room_name = input(
                "Room Name: "
            )

            packet = create_packet(
                GET_HISTORY,
                sender=username,
                room=room_name
            )

            response = send_packet(
                client,
                packet
            )

            print("\nDEBUG RESPONSE")
            print(response)

            history = response[
                "data"
            ][
                "history"
            ]

            print(
                "\n===== CHAT HISTORY ====="
            )

            if not history:

                print(
                    "No messages found."
                )

            else:

                for msg in history:

                    print(
                        f"[{msg['timestamp']}] "
                        f"{msg['sender']}: "
                        f"{msg['message']}"
                    )

        # ======================
        # EXIT
        # ======================

        elif choice == "8":

            room_name = input(
                "Room Name: "
            )

            packet = create_packet(
                LEAVE_ROOM,
                sender=username,
                room=room_name
            )

            response = send_packet(
                client,
                packet
            )

            print(
                "\nSERVER RESPONSE"
            )

            print(response)

        elif choice == "9":

            print(
                "\nDisconnecting..."
            )

            break

    client.close()


if __name__ == "__main__":
    main()
