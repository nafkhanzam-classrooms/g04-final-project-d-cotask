import socket
from xmlrpc import client
import threading

from protocol import *

HOST = "127.0.0.1"
PORT = 5000

current_room = None

def receive_notifications(
    client
):

    while True:

        try:

            response = client.recv(
                4096
            ).decode()

            if not response:

                break

            packet = deserialize(
                response
            )

            if packet[
                "type"
            ] == TASK_NOTIFICATION:

                print(
                    "\n=================="
                )

                print(
                    "NOTIFICATION"
                )

                print(
                    packet["data"]["message"]
                )

                print(
                    "=================="
                )

        except:

            break

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

    client = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    client.connect(
        (HOST, PORT)
    )

    username = ""

    while True:

        print("\n===== COTASK =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("> ")

        if choice == "1":

            username = input(
                "Username: "
            )

            password = input(
                "Password: "
            )

            packet = create_packet(
                REGISTER,
                sender=username,
                data={
                    "password": password
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

        elif choice == "2":

            username = input(
                "Username: "
            )

            password = input(
                "Password: "
            )

            packet = create_packet(
                LOGIN,
                sender=username,
                data={
                    "password": password
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

            if response["type"] == SUCCESS:

                threading.Thread(

                    target=receive_notifications,

                    args=(client,),

                    daemon=True

                ).start()

                print(
                    "\nLogin berhasil!"
                )

                break

        elif choice == "3":

            client.close()

            return

        else:

            print(
                "Pilihan tidak valid!"
            )

    # ==========================
    # MAIN MENU
    # ==========================

    while True:

        print("\n===== MENU =====")
        print("1. Create Room")
        print("2. Join Room")
        print("3. Room List")
        print("4. Enter Room")
        print("5. Online Users")
        print("6. Private Message")
        print("7. View Private Messages")
        print("8. Exit")

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

        # ENTER ROOM
        elif choice == "4":

            room_name = input(
                "Room Name: "
            )

            packet = create_packet(
                ENTER_ROOM,
                sender=username,
                room=room_name
            )

            response = send_packet(
                client,
                packet
            )

            if response["type"] == SUCCESS:

                current_room = room_name

                room_menu(
                    client,
                    username,
                    current_room
                )

            else:

                print(response)

        # ONLINE USERS
        elif choice == "5":

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

        # PRIVATE MESSAGE
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

        # VIEW PRIVATE MESSAGES
        elif choice == "7":
            print(
                "\nBelum diimplementasikan"
            )
    
        # ======================
        # EXIT
        # ======================

        elif choice == "8":

            print(
                "\nDisconnecting..."
            )

            break

        else:

            print(
                "Pilihan tidak valid!"
            )

    client.close()

def room_menu(
    client,
    username,
    current_room
):

    while True:

        print(
            f"\n===== ROOM : {current_room} ====="
        )

        print("1. Broadcast Message")
        print("2. Chat History")

        print("3. Task Board")
        print("4. Create Task")
        print("5. Assign Task")
        print("6. Update Task")

        print("7. Leave Room")
        print("8. Back")

        choice = input("> ")

        # =====================
        # BROADCAST
        # =====================

        if choice == "1":

            message = input(
                "Message: "
            )

            packet = create_packet(
                BROADCAST,
                sender=username,
                room=current_room,
                data={
                    "message": message
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

        # =====================
        # HISTORY
        # =====================

        elif choice == "2":

            packet = create_packet(
                GET_HISTORY,
                sender=username,
                room=current_room
            )

            response = send_packet(
                client,
                packet
            )

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

        # =====================
        # TASK BOARD
        # =====================

        elif choice == "3":

            packet = create_packet(
                TASK_BOARD,
                sender=username,
                room=current_room
            )

            response = send_packet(
                client,
                packet
            )

            task_list = response[
                "data"
            ][
                "tasks"
            ]

            print(
                f"\n===== TASK BOARD ({current_room}) ====="
            )

            if not task_list:

                print(
                    "No task found."
                )

            else:

                for task in task_list:

                    print(
                        f"\n[{task['id']}]"
                    )

                    print(
                        f"Title: "
                        f"{task['title']}"
                    )

                    print(
                        f"Assignee: "
                        f"{task['assignee']}"
                    )

                    print(
                        f"Status: "
                        f"{task['status']}"
                    )

        # =====================
        # CREATE TASK
        # =====================

        elif choice == "4":

            title = input(
                "Task Title: "
            )

            packet = create_packet(
                CREATE_TASK,
                sender=username,
                room=current_room,
                data={
                    "title": title
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

        # =====================
        # ASSIGN TASK
        # =====================
        elif choice == "5":

            task_id = int(
                input(
                    "Task ID: "
                )
            )

            assignee = input(
                "Assign To: "
            )

            packet = create_packet(
                ASSIGN_TASK,
                sender=username,
                room=current_room,
                data={
                    "task_id": task_id,
                    "assignee": assignee
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

        # =====================
        # UPDATE TASK
        # =====================

        elif choice == "6":

            task_id = int(
                input(
                    "Task ID: "
                )
            )

            print(
                "\nAvailable Status:"
            )

            print("1. TODO")
            print("2. IN_PROGRESS")
            print("3. DONE")

            status_choice = input("> ")

            if status_choice == "1":

                status = "TODO"

            elif status_choice == "2":

                status = "IN_PROGRESS"

            elif status_choice == "3":

                status = "DONE"

            else:

                print(
                    "Invalid status"
                )

                continue

            packet = create_packet(
                UPDATE_TASK,
                sender=username,
                room=current_room,
                data={
                    "task_id": task_id,
                    "status": status
                }
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

        # =====================
        # LEAVE ROOM
        # =====================

        elif choice == "7":

            packet = create_packet(
                LEAVE_ROOM,
                sender=username,
                room=current_room
            )

            response = send_packet(
                client,
                packet
            )

            print(response)

            break

        # =====================
        # BACK
        # =====================

        elif choice == "8":

            break

if __name__ == "__main__":
    main()
