import requests
import time
from roomba.create2 import Create2
import pyrebase

roomba = None

DISTANCE = 19
ANGLE = 20

CLIFF_LEFT = 9
CLIFF_FRONT_LEFT = 10
CLIFF_FRONT_RIGHT = 11
CLIFF_RIGHT = 12

BUMPER = 45

WHEEL_DROP = 7

WALL = 8

VELOCITY_LEFT = 42
VELOCITY_RIGHT = 41

LEFT_ENCODER = 43
RIGHT_ENCODER = 44

SENSORS_LIST = [DISTANCE, ANGLE, CLIFF_LEFT, CLIFF_FRONT_LEFT, CLIFF_FRONT_RIGHT, CLIFF_RIGHT, BUMPER, WHEEL_DROP, WALL, VELOCITY_LEFT, VELOCITY_RIGHT, LEFT_ENCODER, RIGHT_ENCODER]


URL = 'https://twilio-plays-roomba.herokuapp.com/next';

config = {
	"apiKey": "AIzaSyD7Br51b3F296kpbD3PcvRbaz1jYaL_Oi8",
	"authDomain": "hacktech2017-2d0d8.firebaseapp.com",
	"databaseURL": "https://hacktech2017-2d0d8.firebaseio.com",
	"storageBucket": "hacktech2017-2d0d8.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#results = db.child("sensors").update({"distance": 8})

def run_command(message):
	try:
		command, degree = message.split()
		command = command.lower()
		degree = float(degree)
		print("Running command: {}".format(message))
		if command == 'forward':
			roomba.straight(degree)
		elif command == 'backward':
			roomba.straight(-1 * degree)
		elif command == 'turn':
			roomba.clockwise(degree)
		elif command == 'turn-':
			roomba.counterclockwise(degree)
		else:
			print("Not a valid command: {}".format(message))
	except Exception as e:
		print e
		print("Error when sending message: {}".format(message))
	finally:
		time.sleep(0.5)
		roomba.drive(0, 0)

def validate(message):
	try:
		command, degree = message.split()
		if command not in ['forward', 'backward', 'turn-', 'turn'] and float(degree) < 0:
			return False
	except Exception as e:
		return False
	return True

def read_sensors():
	sensors = roomba.query_list(SENSORS_LIST)

	data = {
		"sensors/": {
			"angle": sensors.angle,
			"distance": sensors.distance
		},
		"sensors/bumper/": {
			"bumper_center_left": sensors.bumper_center_left,
			"bumper_center_right": sensors.bumper_center_right,
			"bumper_front_left": sensors.bumper_front_left,
			"bumper_front_right": sensors.bumper_front_right,
			"bumper_left": sensors.bumper_left,
			"bumper_right": sensors.bumper_right
		},
		"sensors/cliff/": {
			"cliff_front_left": sensors.cliff_front_left,
			"cliff_front_right": sensors.cliff_front_right,
			"cliff_left": sensors.cliff_left,
			"cliff_right": sensors.cliff_right
		},
		"sensors/encoder/": {
			"encoder_left": sensors.encoder_left,
			"encoder_right": sensors.encoder_right
		},
		"sensors/velocity/": {
			"wheel_left_velocity": sensors.requested_left_velocity,
			"wheel_right_velocity": sensors.requested_right_velocity
		},
		"sensors/wheel_drop/": {
			"wheel_drop_left": sensors.wheel_drop_left,
			"wheel_drop_right": sensors.wheel_drop_right
		}
	}

	print(str(data))
	db.update(data)

def start_client():
	roomba = Create2()
	roomba.start()
	roomba.safe()

	count = 0

	while True:
		if count % 2 == 0:
			read_sensors()
		try:
			res = requests.get(URL).json()
			if 'command' in res:
				command = res['command']
				if validate(command):
					print(command)
					run_command(command)
				else:
					print("Invalid command.")
			else:
				print('No commands in the queue.')
				
		except Exception as e:
			print e
			print 'Invalid request to Twilio'
			continue

		count = count + 1
		time.sleep(1)


if __name__ == '__main__':
	start_client()
