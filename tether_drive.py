#!/usr/bin/env python

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

roomba = Create2()
roomba.start()
roomba.safe()

print "Hold keys to move:"
print "\tw - forward"
print "\ta - left"
print "\td - right"
print "\ts - backward"
print "\tctrl+c - quit"

try:
    tty.setcbreak(sys.stdin.fileno())

    while True:
        if isData():
            char = sys.stdin.read(1)
        else:
            char = -1

        if char == 'w':     
            roomba.straight(300)
        elif char == 'a': 
            roomba.counterclockwise(100)
        elif char == 'd':
            roomba.clockwise(100)   
        elif char == 's':
            roomba.straight(-200) 
        else:
            roomba.drive(0, 0)
	time.sleep(0.05)
        
except:
    traceback.print_exc()

finally:
    termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
    roomba.drive(0,0)
    sys.exit()   
