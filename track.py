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

roomba.straight(499)
time.sleep(5)
roomba.drive(0,0)

