import os
from flask import Flask, request, send_from_directory, json,jsonify
from pygdbmi.gdbcontroller import GdbController
from tlv_server import recv_tlv
import threading
from typing import Any, cast
from werkzeug.exceptions import HTTPException, InternalServerError
import linecache

tlv_lock = threading.Lock()
tlv_messages = []

# Type that describes a parsed response from pygdmi
GdbResponse = list[dict[str, Any]]


def tlv_server_thread():
    while True:
        msg = recv_tlv()
        print(msg)

        tlv_lock.acquire()
        tlv_messages.append(msg)
        tlv_lock.release()


app = Flask(__name__, static_folder="./frontend/build/")

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

# handle post requests from react
@app.route("/api/output", methods=["POST"])
def gdbmi_output():
    input = request.form["submit"]
    # input_array = input.split(" ")
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

# stepping command, steps for whole program
@app.route("/api/step")
def step_info():
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
            line = linecache.getline("demo-multithread.c", num)
    except:
        # command not running
        line = ""
        num = -1
    return jsonify(curr_line=line, line_num = num)

"""
@app.route("/api/variables")
def to_stdout(response):
    print(request.form)
    tid = request.form["thread"]
    output = gdbmi.write(
        f"-stack-list-variables --thread {tid} --frame 0 --all-values"
    )
    return output
"""

# get info about threads
@app.route("/api/threads")
def threads():
    json_threads = []
    res = cast(GdbResponse, gdbmi.write("-thread-info"))[0]
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


# Start the thread that receives updates from the libc interception c code
tlv_thread = threading.Thread(target=tlv_server_thread)
tlv_thread.start()

# Start the flask server
if __name__=="__main__":
    app.run()
