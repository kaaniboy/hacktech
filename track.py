import traceback
import time
import sys
import select
import tty
import termios

from roomba.create2 import Create2

roomba = Create2()
roomba.start()
roomba.safe()

roomba.straight(418)
time.sleep(1.5)
roomba.drive(0, 0)
roomba.clockwise(414)
time.sleep(0.5)
roomba.drive(0, 0)

