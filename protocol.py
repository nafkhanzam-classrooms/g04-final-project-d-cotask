import json
from datetime import datetime

# ==========================================
# PACKET TYPES
# ==========================================

REGISTER = "REGISTER"
LOGIN = "LOGIN"
LOGOUT = "LOGOUT"

ENTER_ROOM = "ENTER_ROOM"
CREATE_ROOM = "CREATE_ROOM"
JOIN_ROOM = "JOIN_ROOM"
LEAVE_ROOM = "LEAVE_ROOM"
ROOM_LIST = "ROOM_LIST"

BROADCAST = "BROADCAST"
PRIVATE_MESSAGE = "PRIVATE_MESSAGE"

TASK_BOARD = "TASK_BOARD"
CREATE_TASK = "CREATE_TASK"
UPDATE_TASK = "UPDATE_TASK"
DELETE_TASK = "DELETE_TASK"
LIST_TASKS = "LIST_TASKS"
GET_HISTORY = "GET_HISTORY"
ASSIGN_TASK = "ASSIGN_TASK"
TASK_NOTIFICATION = "TASK_NOTIFICATION"

ONLINE_USERS = "ONLINE_USERS"

SUCCESS = "SUCCESS"
ERROR = "ERROR"


# ==========================================
# PACKET BUILDER
# ==========================================

def create_packet(
    packet_type,
    sender="",
    room="",
    data=None
):
    """
    Membuat packet dengan format standar
    """

    if data is None:
        data = {}

    packet = {
        "type": packet_type,
        "sender": sender,
        "room": room,
        "timestamp": datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        ),
        "data": data
    }

    return packet


# ==========================================
# SERIALIZATION
# ==========================================

def serialize(packet):
    """
    Dictionary -> JSON String
    """

    return json.dumps(packet)


# ==========================================
# DESERIALIZATION
# ==========================================

def deserialize(message):
    """
    JSON String -> Dictionary
    """

    return json.loads(message)



def packet_success(message):
    return create_packet(
        SUCCESS,
        data={
            "message": message
        }
    )


def packet_error(message):
    return create_packet(
        ERROR,
        data={
            "message": message
        }
    )
