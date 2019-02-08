#!/usr/bin/env python3
'''
Meant to run on your PC.
Receives data generated by rmServerWacomInput.py,
moves the mouse and presses accordingly.
Configure area below!
'''


import socket
import struct
from pynput.mouse import Button, Controller

mouse = Controller()

def mouseMoveAbs(x, y):
	'''The 'mouse.move()' method only moves relative.
	   This funtion works with absolute values.'''
	pos = mouse.position
	mouse.move(x - pos[0], y - pos[1])

# ----------
# Config:

ONLY_DEBUG=False  # Only show data. Don't move mouse

# Area on your display (remember to keep correct ratio (1872:1404 or 312:234) or your input will get streched/squashed!)
SCREEN_DRAW_AREA_FROM_X = 660
SCREEN_DRAW_AREA_FROM_Y = 107
SCREEN_DRAW_AREA_TO_X = 1347  # Ratio will match roughly but not exact!
SCREEN_DRAW_AREA_TO_Y = 1023  # ↑
SCREEN_DRAW_BUTTON_PRESSURE = 1000  # Pressure needed to click the left mouse button (0 contact; 4095 = hardest)

# ----------

WACOM_WIDTH = 15725   # Values just checked by drawing to the edges
WACOM_HEIGHT = 20967  # ↑

screenRectWidth = SCREEN_DRAW_AREA_TO_X - SCREEN_DRAW_AREA_FROM_X
screenRectHeight = SCREEN_DRAW_AREA_TO_Y - SCREEN_DRAW_AREA_FROM_Y
ratioX = screenRectWidth / WACOM_WIDTH
ratioY = screenRectHeight / WACOM_HEIGHT

# Source: https://github.com/canselcik/libremarkable/blob/master/src/input/wacom.rs
EV_SYNC = 0
EV_KEY = 1
EV_ABS = 3
WACOM_EVCODE_PRESSURE = 24
WACOM_EVCODE_DISTANCE = 25
WACOM_EVCODE_XTILT = 26
WACOM_EVCODE_YTILT = 27
WACOM_EVCODE_XPOS = 0
WACOM_EVCODE_YPOS = 1

lastXPos = -1
lastYPos = -1
lastXTilt = -1
lastYTilt = -1
lastDistance = -1
lastPressure = -1

mouseButtonPressed = False

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('10.11.99.1', 33333))

while True:
	evDevType, evDevCode, evDevValue = struct.unpack('HHi', client.recv(8))
	if evDevType == EV_ABS:
		if evDevCode == WACOM_EVCODE_XPOS:
			lastYPos = evDevValue  # X is Y
		elif evDevCode == WACOM_EVCODE_YPOS:
			lastXPos = evDevValue  # Y is X
		elif evDevCode == WACOM_EVCODE_XTILT:
			lastXTilt = evDevValue
		elif evDevCode == WACOM_EVCODE_YTILT:
			lastYTilt = evDevValue
		elif evDevCode == WACOM_EVCODE_DISTANCE:
			lastDistance = evDevValue
		elif evDevCode == WACOM_EVCODE_PRESSURE:
			if not ONLY_DEBUG:
				if not mouseButtonPressed and evDevValue > SCREEN_DRAW_BUTTON_PRESSURE:
					mouse.press(Button.left)
					mouseButtonPressed = True
				elif mouseButtonPressed and evDevValue <= SCREEN_DRAW_BUTTON_PRESSURE:
					mouse.release(Button.left)
					mouseButtonPressed = False

			lastPressure = evDevValue

		if ONLY_DEBUG:
			print('XPos: %5d | YPos: %5d | XTilt: %5d | YTilt: %5d | Distance: %3d | Pressure: %4d' % (lastXPos, lastYPos, lastXTilt, lastYTilt, lastDistance, lastPressure))
		else:
			screenX = SCREEN_DRAW_AREA_FROM_X + round(lastXPos * ratioX)                   # (X doesn't need to invert)
			screenY = SCREEN_DRAW_AREA_FROM_Y + round((WACOM_HEIGHT - lastYPos) * ratioY)  # (Y has to be inverted)
			mouseMoveAbs(screenX, screenY)

