from flask import Flask, render_template, request
from pygdbmi.gdbcontroller import GdbController
# takes in input of file to run
# starts gdbmi instance, then 

app = Flask(__name__)

# Start up pygdmi
gdbmi = GdbController()

# use POST for commands - take an argument (command), run it, then give all
# output back to host
@app.route("/")
def input():
    return render_template('input-command.html')

@app.route("/output", methods=['POST'])
def output():
    input = request.form['command']
    output = "invalid command"
    if input == "start":
        output = to_stdout(gdbmi.write('-file-exec-and-symbols a.out'))
    elif input == "run":
        output = to_stdout(gdbmi.write('-exec-run'))
    return output

# look for messages to stdout
def to_stdout(response):
    output = ''
    for json in response:
        if json['stream'] == 'stdout' and json['message'] != None:
            output = output + json['message'] + '<br>'
    return output

# @app.route("/")
app.run()