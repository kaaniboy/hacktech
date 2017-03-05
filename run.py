from flask import Flask, request, redirect
import twilio.twiml
import traceback
import time
import sys
import select
import tty
import termios
from roomba.create2 import Create2

def isData():
    return select.select([sys.stdin], [], [], 0) == ([sys.stdin], [], [])

old_settings = termios.tcgetattr(sys.stdin)

#roomba = Create2()
#roomba.start()
#roomba.safe()

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def hello_monkey():
    """Respond to incoming calls with a simple text message."""
    roomba = Create2()
    roomba.start()
    roomba.safe()

    response = ""
    msg = request.values.get('Body', None)
    arrayMsg = msg.split()
    secondArg = float(arrayMsg[1])
    print(msg)
    print(arrayMsg)
    if "forward" in msg:
      roomba.straight(secondArg)
    elif "backward" in msg:
      roomba.clockwise(180)
      roomba.straight(secondArg)
    elif "turn-" in msg:
      print("Success Turn ", secondArg)
      roomba.counterclockwise(secondArg)
    elif "turn" in msg:
      roomba.clockwise(secondArg)
    else:
      roomba.drive(0,0)

    time.sleep(0.5)
    roomba.drive(0, 0)   
    resp = twilio.twiml.Response()
    resp.message(msg)
    return str(resp)

if __name__ == "__main__":
    app.run(debug=True)
