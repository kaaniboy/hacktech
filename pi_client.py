import requests
import time
from roomba.create2 import Create2
import pyrebase
from subprocess import call
import random, string
import math
import httplib, urllib, base64, json

roomba = Create2()
roomba.start()
roomba.safe()
roomba.full()

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


URL = 'http://twilio-plays.herokuapp.com/next';

config = {
	"apiKey": "AIzaSyD7Br51b3F296kpbD3PcvRbaz1jYaL_Oi8",
	"authDomain": "hacktech2017-2d0d8.firebaseapp.com",
	"databaseURL": "https://hacktech2017-2d0d8.firebaseio.com",
	"storageBucket": "hacktech2017-2d0d8.appspot.com"
}

headers = {
    'Content-Type': 'application/octet-stream',
    'Ocp-Apim-Subscription-Key': '412f4f821283482ab9bd2fe62ca387b6',
}

params = urllib.urlencode({
    'visualFeatures': 'Categories',
    'details': 'Celebrities',
    'language': 'en',
})

firebase = pyrebase.initialize_app(config)
db = firebase.database()
storage = firebase.storage()

x = 0
y = 0
angle = 0

def approx_angle(input):
	return 0.1778 * input + 16.46
def approx_dist(input):
	return 0.05186 * input + 2.452

def to_rad(degrees):
	return degrees * math.pi / 180

def update_position(dist, ang):
	global x
	global y

	if ang > 0 and ang < 90:
		x = x + dist * math.sin(to_rad(ang))
		y = y + dist * math.cos(to_rad(ang))
	elif ang > 90 and ang < 180:
		x = x + dist * math.cos(to_rad(ang - 90))
		y = y - dist * math.sin(to_rad(ang - 90))
	elif ang > 180 and ang < 270:
		x = x - dist * math.cos(to_rad(ang - 180))
		y = y - dist * math.sin(to_rad(ang - 180))
	elif ang > 270 and ang < 360:
		x = x - dist * math.cos(to_rad(ang - 270))
		y = y + dist * math.sin(to_rad(ang - 270))
	elif ang == 0:
		y = y + dist
	elif ang == 90:
		x = x + dist
	elif ang == 180:
		y = y - dist
	elif ang == 270:
		x = x - dist

	print("Angle: ", ang)
	print("X: ", x)
	print("Y: ", y)

	db.child('/roomba_position').update({'x': x, 'y': y})

def run_command(message):
	global angle

	try:
		command, degree = message.split()
		command = command.lower()
		degree = float(degree)
		print("Running command: {}".format(message))
		if command == 'forward':
			roomba.straight(degree)
			update_position(approx_dist(degree), angle)
			time.sleep(1.5)
		elif command == 'backward':
			roomba.straight(-1 * degree)
			update_position(-1 * approx_dist(degree), angle)
			time.sleep(1.5)
		elif command == 'turn':
			roomba.clockwise(degree)
			angle = (angle + approx_angle(degree)) % 360
			time.sleep(0.5)
		elif command == 'turn-':
			roomba.counterclockwise(degree)

			if angle - approx_angle(degree) < 0:
				angle = angle + 360 - approx_angle(degree)
			else:
				angle = angle - approx_angle(degree)

			time.sleep(0.5)
		else:
			print("Not a valid command: {}".format(message))
	except Exception as e:
		print e
		print("Error when sending message: {}".format(message))
	finally:
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
		"bumper/": {
			"bumper_center_left": sensors.light_bumper_center_left,
			"bumper_center_right": sensors.light_bumper_center_right,
			"bumper_front_left": sensors.light_bumper_front_left,
			"bumper_front_right": sensors.light_bumper_front_right,
			"bumper_left": sensors.light_bumper_left,
			"bumper_right": sensors.light_bumper_right
		},
		"cliff/": {
			"cliff_front_left": sensors.cliff_front_left,
			"cliff_front_right": sensors.cliff_front_right,
			"cliff_left": sensors.cliff_left,
			"cliff_right": sensors.cliff_right
		},
		"encoder/": {
			"encoder_left": sensors.left_encoder_count,
			"encoder_right": sensors.right_encoder_count
		},
		"velocity/": {
			"wheel_left_velocity": sensors.requested_left_velocity,
			"wheel_right_velocity": sensors.requested_right_velocity
		},
		"wheel_drop/": {
			"wheel_drop_left": sensors.wheel_drop_left,
			"wheel_drop_right": sensors.wheel_drop_right
		}
	}

	db.update(data)

def analyzeImage(filename):
	try:
    		f = open(filename, "rb")
        	body = f.read()
        	f.close()
        	conn = httplib.HTTPSConnection('westus.api.cognitive.microsoft.com')
        	conn.request("POST", "/vision/v1.0/analyze?%s" % params, body, headers)
        	response = conn.getresponse()
        	data = response.read()
        	results = db.child("vision").update({"data": json.loads(data)})
        	conn.close()
	except Exception as e:
        	print("[Errno {0}] {1}".format(e.errno, e.strerror))

def randomword(length):
	return ''.join(random.choice(string.lowercase) for i in range(length))

def take_photo():
	file_name = randomword(10) + '.jpg'
	call(['fswebcam', file_name])
	storage.child("images/" + file_name).put(file_name)
	db.child("newest_image/").update({"image_name": file_name})
	analyzeImage(file_name)

def start_client():
	count = 0

	while True:
		if count % 4 == 0:
			read_sensors()
		if count % 5 == 0:
			take_photo()
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
	print('Starting...')
	start_client()
