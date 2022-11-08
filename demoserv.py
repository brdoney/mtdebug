import os
from flask import Flask, request, send_from_directory, json

# from pygdbmi.gdbcontroller import GdbController
from gdb_websocket import GdbController
from tlv_server import recv_tlv
import threading
from typing import Any, Optional, cast
from werkzeug.exceptions import HTTPException, InternalServerError

tlv_lock = threading.Lock()
tlv_messages = []

# Type that describes a parsed response from pygdmi
GdbResponseEntry = dict[str, Any]
GdbResponse = list[GdbResponseEntry]


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


@app.route("/api/output", methods=["POST"])
def output():
    input = request.form["command"]
    output = "invalid command"
    if input == "start":
        output = to_stdout(gdbmi.write("-file-exec-and-symbols multithread-demo"))
        gdbmi.write("b 29")
    elif input == "run":
        output = to_stdout(gdbmi.write("-exec-run"))
    elif input == "variables":
        print(request.form)
        tid = request.form["thread"]
        output = gdbmi.write(
            f"-stack-list-variables --thread {tid} --frame 0 --all-values"
        )
    return output


# look for messages to stdout
def to_stdout(response):
    print("Getting stdout:", response)
    output = ""
    for msg in response:
        if msg["stream"] == "stdout" and msg["message"] is not None:
            output = output + msg["message"] + "<br>"
    return output


def get_result(response: GdbResponse) -> Optional[GdbResponseEntry]:
    print("Getting result:", response)
    for msg in response:
        if msg["type"] == "result":
            return msg
    return None


@app.route("/api/threads")
def threads():
    all_res = gdbmi.write("-thread-info")
    res = cast(GdbResponse, all_res)
    res = get_result(res)
    if res is None:
        print(all_res, res)
        raise InternalServerError("Could not fetch threads")
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


@app.before_first_request
def start_threads():
    # Start the thread that receives updates from the libc interception c code
    tlv_thread = threading.Thread(target=tlv_server_thread)
    tlv_thread.start()


# Start the flask server
app.run()
