# Main module or, in other words, brain of the robot
from cv import game_state as cv
from ik import ik
import mappings as m
import time
import cv2
import numpy as np

def main(screen_view = False):
	processor = cv.module_init(screen_view)
	serial_com = ik.module_init()
	time.sleep(1)
	print "Everything initialised"
	# First iteration
	if screen_view:
            frames = processor.next()
            ball_coords = frames[-3]
	    basket_coord = frames[-2]
	    score = frames[-1]
	    bin_gray = cv2.cvtColor(frames[0], cv2.COLOR_GRAY2BGR)
	    frames = np.hstack((frames[1],bin_gray))
	    cv2.imshow('frame', frames)
	else:
            ball_coords, basket_coords, score = processor.next()
	action = m.GRID_TO_ACTIONS[ball_coords[0]]
	position = m.GRID_TO_COORDINATES[ball_coords[0]]
	ik.send_position(serial_com, position)
	ik.send_action(serial_com, action)
	while True:
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break


if __name__ == '__main__':
	main(screen_view = True)