# This module should be able to receive the position of 
# the ball and the basket, drive the arm to that position
# and then send the action to be performed
import serial

BAUDRATE = 9600
PORT = '/dev/ttyACM0'
Y_COORD = '955\n'
Z_COORD = '61\n'


def module_init():
	print "Starting serial comunication"
	ser = serial.Serial(PORT, BAUDRATE)
	return serial

def send_action(serial_com, action):
	"""
	Function that sends an action to the Arduino through
	the serial port.

	:param serial_com: serial object to communicate with the Arduino
	:param action: int with the action to be performed
	"""
	act = 'A'+str(action)+'\n'
	print "Sending action: "+act
	serial_com.write(act)

def send_position(serial_com, position):
	"""
	Function that drives the arm to the desired position. It only
	needs the x position because y and z are fixed coordinates

	:param serial_com:
	"""
	print "Sending arm coordinates: "+"X - "+str(position)
	# send x coordinate
	serial_com.write(str(position)+'2\n')
	# send y coordinate
	serial_com.write(Y_COORD)
	#send z coordinate
	serial_com.write(Z_COORD)

