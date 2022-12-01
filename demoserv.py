import os
from typing import Any, Optional, cast
from time import time
import threading
import linecache
import functools

from gdb_websocket import GdbController
from tlv_server import recv_tlv

from flask import Flask, request, send_from_directory, json, jsonify
from werkzeug.exceptions import BadRequest, HTTPException

import asyncio
from websockets import server as wsserver
import websockets

tlv_lock = threading.Lock()
tlv_messages = []

# Type that describes a parsed response from pygdmi
GdbResponseEntry = dict[str, Any]
GdbResponse = list[GdbResponseEntry]

# Port for websocket used for communicating to GDB TUI
WEBSOCKET_PORT = 5001


def tlv_server_thread():
    while True:
        msg = recv_tlv()
        print(msg)

        tlv_lock.acquire()
        tlv_messages.append(msg)
        tlv_lock.release()


app = Flask(__name__, static_folder="./frontend/build/")
app.debug = True

# Start up pygdmi
gdbmi = GdbController()


@app.errorhandler(HTTPException)
def handle_exception(e):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = e.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": e.code,
            "name": e.name,
            "description": e.description,
        }
    )
    response.content_type = "application/json"
    return response


# Serve React App
@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve(path):
    if app.static_folder is None:
        raise Exception(
            "static folder was not set; must point to frontend build directory"
        )

    if path != "" and os.path.exists(app.static_folder + "/" + path):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, "index.html")


@app.post("/api/start")
def start_program():
    gdbmi.write("-file-exec-and-symbols multithread-demo")
    gdbmi.write("b main")
    output = gdbmi.write("-exec-run")
    return output


@app.post("/api/exec")
def control_execution():
    # TODO: Implement global execution-controlling instructions w/ -a flag

    json = request.get_json()
    action = json["action"]
    thread = json["thread"]

    if action == "step":
        output = gdbmi.write(f"-exec-step --thread {thread}")
    elif action == "next":
        output = gdbmi.write(f"-exec-next --thread {thread}")
    elif action == "finish":
        output = gdbmi.write(f"-exec-finish --thread {thread}")
    elif action == "continue":
        output = gdbmi.write(f"-exec-continue --thread {thread}")
    elif action == "stop":
        output = gdbmi.write(f"-exec-return --thread {thread}")
    else:
        return None
    return output  # type: ignore


@app.post("/api/breakpoint")
def handle_breakpoint():
    json = request.get_json()
    symbol = json["symbol"]
    return gdbmi.write(f"b {symbol}")


@app.get("/api/step/<int:thread_id>")
def step_info(thread_id: int):
    """Stepping command, steps for whole program."""
    line = ""
    num = -1
    try:
        # get stack frame info
        res = gdbmi.write(f"-stack-info-frame --thread {thread_id}")
        res = cast(GdbResponse, res)[0]
        frame = {}
        line = ""

        # print current line of execution
        if res["message"] != "error":
            frame = res["payload"]["frame"]
            num = int(frame["line"])
            line = linecache.getline("./examples/multithread-demo.c", num)
    except Exception:
        # TODO: Slim down what we're catching to just be what is raised
        # command not running
        line = ""
        num = -1
    return jsonify(curr_line=line, line_num=num)


def get_result(response: GdbResponse) -> Optional[GdbResponseEntry]:
    for msg in response:
        if msg["type"] == "result":
            return msg
    return None


@app.route("/api/threads")
def threads():
    """Get info about threads."""
    all_res = gdbmi.write("-thread-info")
    res = cast(GdbResponse, all_res)
    res = get_result(res)

    """
    threads = res["payload"]["threads"]
    if res["message"] != "done":
        raise InternalServerError("Could not fetch threads")
    if res["payload"]["threads"] != []:
        for thread in threads:
            curr_vars = []
            tid = int(thread["id"])
            output = cast(GdbResponse, gdbmi.write(
            f"-stack-list-variables --thread {tid} --frame 0 --all-values"))[0]
            output_list = output["payload"]["variables"]
            for vars in output_list:
                for var in vars:
                    if var != 'none':
                        curr_vars.append(var)
            json_threads.append({"tid":tid, "vars": curr_vars, "target-id":thread["target-id"]})
    """
    return res["payload"]["threads"]


@app.route("/api/msg")
def messages():
    tlv_lock.acquire()
    if len(tlv_messages) > 0:
        val = tlv_messages
    else:
        val = "No messages yet"
    tlv_lock.release()

    return str(val)


async def watch_gdb(ws: wsserver.WebSocketServerProtocol):
    loop = asyncio.get_running_loop()
    read_call = functools.partial(gdbmi.read, using_mi=False, timeout_sec=0)

    while True:
        # Have to run in executor b/c it will block thread (other async calls will be
        # stuck until unblocked)
        output = await loop.run_in_executor(None, read_call)
        print("out:", output)

        # Send the TUI output to the frontend for rendering
        try:
            await ws.send(output)
        except websockets.ConnectionClosedOK:
            break


async def watch_ws(ws: wsserver.WebSocketServerProtocol) -> None:
    while True:
        try:
            res: bytes | str = await ws.recv()
        except websockets.ConnectionClosedOK:
            break

        # If we had a string frame (not a byte frame), then have to encode to bytes
        if isinstance(res, str):
            res = str.encode(res, "ascii")
        print("in:", res, type(res))

        # Send the user input to the GDB TUI instance
        gdbmi.write(res, using_mi=False)


async def watch_gdb_ws(ws: wsserver.WebSocketServerProtocol):
    """Start watching GDB for output (pty stdout -> websocket) and websocket for user
    input (websocket -> pty stdin)."""
    await asyncio.gather(watch_gdb(ws), watch_ws(ws))


async def serve_gdb():
    async with wsserver.serve(
        watch_gdb_ws, "localhost", WEBSOCKET_PORT, reuse_address=True, reuse_port=True
    ):
        print(f"Serving {WEBSOCKET_PORT}")
        await asyncio.Future()  # run forever


@app.get("/api/websocket")
def websocket():
    """API endpoint to start a websocket and get its port (we should eventually switch
    to full addresses)."""
    ws_thread = threading.Thread(target=asyncio.run, args=[serve_gdb()])
    ws_thread.start()
    return {"port": WEBSOCKET_PORT}


@app.before_first_request
def start_threads():
    # Start the thread that receives updates from the libc interception c code
    tlv_thread = threading.Thread(target=tlv_server_thread)
    tlv_thread.start()


# Start the flask server
if __name__ == "__main__":
    app.run()
