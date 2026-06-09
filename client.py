import socket
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
        print("4. Leave Room")
        print("5. Broadcast Chat")
        print("6. Exit")

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

        # ======================
        # EXIT
        # ======================

        elif choice == "4":

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

            client.send(
                serialize(packet).encode()
            )

        elif choice == "6":

            print(
                "\nDisconnecting..."
            )

            break

    client.close()


if __name__ == "__main__":
    main()