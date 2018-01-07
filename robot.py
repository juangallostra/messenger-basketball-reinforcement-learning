# Main module or, in other words, brain of the robot
from cv import game_state as cv
from ik import ik
import mappings as m
import time

def main():
	processor = cv.module_init(screen_view = False)
	serial_com = ik.module_init()
	time.sleep(5)
	print "Everything initialised"
	# First iteration
	ball_coords, basket_coords, score = processor.next()
	action = m.GRID_TO_ACTIONS[ball_coords[0]]
	position = m.GRID_TO_COORDINATES[ball_coords[0]]
	while True:
		ik.send_position(serial_com, position)
		ik.send_action(serial_com, action)

if __name__ == '__main__':
	main()