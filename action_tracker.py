import dataclasses
import threading
from typing import Optional

from flask import jsonify
from flask.wrappers import Response

from tlv_server import LibcAction, TLVTag


@dataclasses.dataclass()
class Resource:
    owner: Optional[int]
    waiters: set[int]


__tracking_lock = threading.Lock()
__resources: dict[str, Resource] = {}


def __track_claim_mutex(action: LibcAction, resources: dict[str, Resource]):
    r = resources[action.address]
    r.waiters.remove(action.thread)
    r.owner = action.thread


def __track_lock_mutex(action: LibcAction, resources: dict[str, Resource]):
    if action.address not in resources:
        resources[action.address] = Resource(None, {action.thread})
    else:
        resources[action.address].waiters.add(action.thread)


def __track_unlock_mutex(action: LibcAction, resources: dict[str, Resource]):
    resources[action.address].owner = None


def track_action(action: LibcAction):
    global __resources, __tracking_lock

    print("Resources", __resources)

    __tracking_lock.acquire()
    op = action.tag
    if op == TLVTag.MUTEX_LOCK:
        __track_lock_mutex(action, __resources)
    elif op == TLVTag.MUTEX_CLAIM:
        __track_claim_mutex(action, __resources)
    elif op == TLVTag.MUTEX_UNLOCK:
        __track_unlock_mutex(action, __resources)
    __tracking_lock.release()


def resource_state() -> Response:
    global __resources

    __tracking_lock.acquire()
    resp = jsonify(__resources)
    __tracking_lock.release()
    return resp
