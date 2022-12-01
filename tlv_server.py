import enum
import socket
import os
import struct
import dataclasses
from typing import Any, Optional

from flask.json import JSONEncoder

TLV_LEN = 16
TLV_PREFIX_LEN = struct.calcsize("!ii")
TLV_MESSAGE_LEN = TLV_LEN - TLV_PREFIX_LEN
print(TLV_LEN, TLV_PREFIX_LEN, TLV_MESSAGE_LEN)

__server: Optional[socket.socket] = None


@enum.unique
class TLVTag(enum.Enum):
    MUTEX_LOCK = 0
    MUTEX_UNLOCK = 1


@dataclasses.dataclass
class TLVMessage:
    tag: TLVTag
    length: int
    value: str


class TLVJSONEncoder(JSONEncoder):
    def default(self, obj: Any) -> Any:
        if isinstance(obj, TLVTag):
            return obj.name
        elif isinstance(obj, TLVMessage):
            return obj.__dict__
        return super().default(obj)


def __parse_tlv(message: bytes, remaining_len=None) -> TLVMessage:
    tag: int
    length: int
    value: bytes
    (tag, length, value) = struct.unpack(f"!ii{TLV_MESSAGE_LEN}s", message)

    if length < TLV_MESSAGE_LEN:
        value = value[:length]
    elif remaining_len is not None:
        value = value[:remaining_len]

    str_value = value.decode("ascii")

    tlv_tag = TLVTag(tag)  # type: ignore

    return TLVMessage(tlv_tag, length, str_value)


def recv_tlv() -> TLVMessage:
    # Start the server if it wasn't already started
    if __server is None:
        __open_socket()

    # At this point, we know we have a valid socket
    conn, _ = __server.accept()  # type: ignore

    length_remaining = None

    # Defaults so we can construct a TLVMessage later
    tag = TLVTag.MUTEX_LOCK
    full_length = 0
    message = ""

    while length_remaining is None or length_remaining > 0:
        data = conn.recv(TLV_LEN)

        if length_remaining is not None and length_remaining < TLV_MESSAGE_LEN:
            tlv = __parse_tlv(data, length_remaining)
        else:
            tlv = __parse_tlv(data)

        if length_remaining is None:
            full_length = tlv.length
            length_remaining = full_length - TLV_MESSAGE_LEN
            message = tlv.value
        else:
            length_remaining -= TLV_MESSAGE_LEN
            message += tlv.value

    conn.close()

    return TLVMessage(tag, full_length, message)


def __open_socket():
    global __server

    if __server is not None:
        return

    if os.path.exists("/tmp/socket_test.s"):
        os.unlink("/tmp/socket_test.s")

    __server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    __server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    __server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    __server.bind("/tmp/socket_test.s")

    __server.listen(1)


def close_socket():
    global __server

    if __server is not None:
        __server.close()
        __server = None
