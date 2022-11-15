import os
from typing import Any, Optional, cast
import threading
import linecache

from gdb_websocket import GdbController
from tlv_server import recv_tlv

from flask import Flask, request, send_from_directory, json, jsonify
from werkzeug.exceptions import HTTPException
from pygdbmi.constants import GdbTimeoutError

import asyncio
from websockets import server as wsserver

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


@app.post("/api/output")
def gdbmi_output():
    """Handle post requests from react"""
    input = request.form["submit"]
    output = []
    if input == "start":  # start gdb execution, set breakpoint on main
        gdbmi.write("-file-exec-and-symbols multithread-demo")
        gdbmi.write("b main")
        output = gdbmi.write("-exec-run")
    elif input == "variables":   # variables command (to be deprecated)
        print(request.form)
        tid = request.form["thread"]
        output = gdbmi.write(
            f"-stack-list-variables --thread {tid} --frame 0 --all-values"
        )
    elif input == "step":
        output = gdbmi.write("-exec-step")
    elif input == "breakpoint":
        input = request.form["breakpoint"]   # get line to break at
        output = gdbmi.write("b " + input)
    elif input == "continue":
        output = gdbmi.write("-exec-continue")
    elif input == "stop":
        output = gdbmi.write("-exec-return")
    return output


@app.get("/api/step")
def step_info():
    """Stepping command, steps for whole program."""
    line = ""
    num = -1
    try:
        # get stack frame info
        res = cast(GdbResponse, gdbmi.write("-stack-info-frame"))[0]
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
    if res is None:
        print(all_res, res)

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


async def watch_gdb(ws) -> None:
    while True:
        try:
            res: bytes | str = await asyncio.wait_for(ws.recv(), 1)

            # If we had a string frame (not a byte frame), then have to encode to bytes
            if isinstance(res, str):
                res = str.encode(res, "ascii")
            print("in:", res, type(res))

            # Send the user input to the GDB TUI instance
            gdbmi.write(res, using_mi=False)
        except asyncio.TimeoutError:
            pass

        try:
            output = gdbmi.read(using_mi=False)
            print("out:", output)

            # Send the TUI output to the frontend for rendering
            await ws.send(output)
        except GdbTimeoutError:
            pass


async def serve_gdb():
    async with wsserver.serve(
        watch_gdb, "localhost", WEBSOCKET_PORT, reuse_address=True, reuse_port=True
    ):
        print(f"Serving {WEBSOCKET_PORT}")
        await asyncio.Future()  # run forever


def start_serve_websocket():
    asyncio.run(serve_gdb())


@app.get("/api/websocket")
def websocket():
    """API endpoint to start a websocket and get its port (we should eventually switch
    to full addresses)."""
    ws_thread = threading.Thread(target=start_serve_websocket)
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
