from flask import Flask, jsonify, request
from flask import render_template
#from dotenv import load_dotenv, find_dotenv
from twilio import twiml

from collections import deque
from threading import Thread
from time import sleep
import os


app = Flask(__name__)

#load_dotenv(find_dotenv())

directions = ['forward', 'backward']

task_q = deque()
"""def send_rasp(task_q):
	while True:
		sleep(2)
		if task_q.empty():
			continue
		message = task_q.get()
		print(message)
		handle_twilio_message(message)

rasp_signal = Thread(target=send_rasp, args=(task_q, ))
rasp_signal.setDaemon(True)
rasp_signal.start()"""

help_message = '''
Twilio Plays Roomba!

COMMANDS:

turn [degree] : turns the roomba X number of positive degrees

turn- [degree] : turns the roomba X number of negative degrees

forward : moves the roomba forward

backward : moves the roomba backward
'''

def validate(message):
	try:
		command, degree = message.split()
		if command not in ['forward', 'backward', 'turn-', 'turn'] or float(degree) < 0:
			return False
	except Exception as e:
		return False
	return True

@app.route('/', methods=['POST'])
def roomba_command():
	twilio_resp = twiml.Response()
	body = request.form['Body']
	message = 'Command valid and queued to roomba! Text howto to see all the commands'
	if body.lower() == 'howto':
		message = help_message
	elif not validate(body):
		message = 'Invalid command try again \n\n {}'.format(help_message)
	else:
		task_q.append(body)
	twilio_resp.message(message)
	return str(twilio_resp)

@app.route('/next', methods=['GET'])
def next():
	if not task_q:
		return jsonify({})
	return jsonify({'command': task_q.popleft()})

@app.route('/queue', methods=['GET'])
def queue():
	return jsonify(list(task_q))

@app.route('/', methods=['GET'])
def index():
	return render_template('index.html')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.debug = True
    app.run(host='0.0.0.0', port=port)
