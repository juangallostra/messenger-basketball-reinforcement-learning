# Main module or, in other words, brain of the robot
from cv import game_state as cv
from ik import ik
from learning import learning as l
import mappings as m
import time
import cv2
import numpy as np
import random

def main(screen_view = False):
	processor = cv.module_init(screen_view)
	serial_com = ik.module_init()
	q_learning = l.Learning()
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
	position = m.GRID_TO_COORDINATES[ball_coords[0]]
	action = q_learning.choose_action(ball_coords[0])
	ik.send_position(serial_com, position)
	ik.send_action(serial_com, action)
	while 1:
		# wait for everything to settle down again
		time.sleep(5)
		# Get info from CV module
		previous_state = ball_coords[0]
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

        # update q
        q_learning.update_q(previous_state, action, score)
        # choose following action
        q_learning.choose_action(ball_coords[0])
        # get position
        position = m.GRID_TO_COORDINATES[ball_coords[0]]
        # perform action
		ik.send_position(serial_com, position)
		ik.send_action(serial_com, action)


if __name__ == '__main__':
	main(screen_view = True)