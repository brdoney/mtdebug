from flask import Flask, render_template, request
from pygdbmi.gdbcontroller import GdbController
from tlv_server import recv_tlv
import threading

tlv_lock = threading.Lock()
tlv_messages = []


def tlv_server_thread():
    while True:
        msg = recv_tlv()
        print(msg)

        tlv_lock.acquire()
        tlv_messages.append(msg)
        tlv_lock.release()


app = Flask(__name__)

# Start up pygdmi
gdbmi = GdbController()


@app.route("/")
def input():
    # use POST for commands - take an argument (command), run it, then give all
    # output back to host
    return render_template("input-command.html")


@app.route("/output", methods=["POST"])
def output():
    input = request.form["command"]
    output = "invalid command"
    if input == "start":
        output = to_stdout(gdbmi.write("-file-exec-and-symbols a.out"))
    elif input == "run":
        output = to_stdout(gdbmi.write("-exec-run"))
    return output


# look for messages to stdout
def to_stdout(response):
    output = ""
    for json in response:
        if json["stream"] == "stdout" and json["message"] is not None:
            output = output + json["message"] + "<br>"
    return output


@app.route("/msg")
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
app.run()
