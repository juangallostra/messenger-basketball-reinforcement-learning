# Theoretically, the info we need from this module is the
# current score and ball and basket state

import cv2
import numpy as np
import pytesseract as ps
from PIL import Image
# for testing purposes
import time
import os

# RQUIRED CONSTANTS
# Estimated areas (should be tuned) to detect ball and basket
BALL_AREA_THRES = (0, 1250)
BASKET_AREA_THRES = (700, 900)
# Regions of interest where ball, basket and score should be found
BALL_ROI = ((0, 202), (250, 360))
BASKET_ROI = ((0, 202), (50, 200))
NUMBERS_ROI = ((0, 202), (200, 275))
FAIL_ROI = ((0,202),(150, 200))
# Basket area and ball area grid definition for state definition
X_BALL_DIVISIONS = 7
Y_BALL_DIVISIONS = 1
X_BASKET_DIVISIONS = 9
Y_BASKET_DIVISIONS = 9
# Rest of constants 
BALL = "ball"
BASKET = "basket"
NUMBERS = '1234567890'

def process_video(source = 0, screen_view = True):
	"""
	This generator is given a video source, reads from it until 
	key "q" is pressed and while not, it yields the ball center coordinates,
	the basket center coordinates and, if required, the current score.
	It is defined as a generator so that the video processing loop
	can be separated from the rest of the program logic

	:param source: int or string str indicating the video source
	:param screen_view: bool value that indicates if what is happening should be shown
	:yields (ball_center, basket_center, score): tuple with the found centers and score or None
	"""
	cap = cv2.VideoCapture(source)
	find_ball_center = find_center(BALL, 6)
	find_basket_center = find_center(BASKET, 1)
	new_score = True
	only_get_score = False
	while(cap.isOpened()):
		ret, frame = cap.read()
		measured_time = time.time()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		_, binarized = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		ball_center, basket_center = find_centers(binarized,
												  find_ball_center,
												  find_basket_center)
		if ball_center and basket_center:
			basket_coords = grid_coordinates(BASKET_ROI, X_BASKET_DIVISIONS, Y_BASKET_DIVISIONS, basket_center)
			ball_coords = grid_coordinates(BALL_ROI, X_BALL_DIVISIONS, Y_BALL_DIVISIONS, ball_center)
			if new_score:
				score = get_score(frame)
				# if score returns a number we assume it is correct.
				# We trust you tesseract, do not fail us.
				if score:
					new_score = False
		else:
			new_score = True

		if screen_view:
			# if the result is to be visualised then we draw the
			# circles marking the computed positions and yield
			# the images as well as the positions and score
			if ball_center:
				cv2.circle(frame,ball_center,2,(0,0,255),3)
			if basket_center:
				cv2.circle(frame,basket_center,2,(255,0,0),3)
			frame = _draw_grid(frame, BALL_ROI, X_BALL_DIVISIONS, Y_BALL_DIVISIONS)
			frame = _draw_grid(frame, BASKET_ROI, X_BASKET_DIVISIONS, Y_BASKET_DIVISIONS)
			yield (binarized, frame, ball_coords, basket_coords, score)
			continue

		if only_get_score:
			only_get_score = yield (score)
		else:
			only_get_score = yield (ball_coords, basket_coords, score)
		continue
	cap.release()
	cv2.destroyAllWindows()

def find_centers(binary_img, find_ball_center, find_basket_center):
	"""
	Function that returns both the ball and basket center. If the ball center is
	not found in the ROI it means that the user already shot the ball. Then there
	is no point in estimating the basket center position and hence it is not computed.

	:param binary_img: np.array with the representation of the binarized image
	:param find_ball_center: function that returns the ball center
	:param find_basket_center: function that returns the basket center
	:returns (ball_center, basket_center): tuple with the coordinates of the centers if found else (None, None)
	"""
	ball_center  = find_ball_center(binary_img)
	# basket center should return only the true center
	# only perform basket detection if ball has been previously found in ROI. 
	if ball_center:
		basket_center = find_basket_center(binary_img)
		return (ball_center, basket_center)
	else:
		return (None, None)


def find_center(element, iterations):
	"""
	Closure that expects an element to search for as input and returns
	a function able to find the center of that element in an image

	:param element: str with value "ball"/"basket" that specifies the element to search for
	:param iterations: int with the number of times the morphological operation should be performed
	:returns find_center: function that searchs for the specified element with the given parameters 
	"""
	# Define morphological operation, structuruing element
	# and threshold depending on what are we looking for
	if element == BASKET:
		el = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))	
		THRESHOLDS = BASKET_AREA_THRES
		morphological_operation = cv2.erode
		roi = BASKET_ROI
	elif element == BALL:
		el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
		THRESHOLDS = BALL_AREA_THRES
		morphological_operation = cv2.dilate
		roi = BALL_ROI
	def _find_center(image):
		"""
		This function, once having defined the required values of the element
		we are looking for, searchs for that element in the region of
		interest and returns its center

		:param image: np.array of the binarized image to be processed
		returns center: tuple with coordinates of the center of the found element or None
		"""
		# apply morphological operation to region of interest
		image = image[roi[1][0]:roi[1][1], roi[0][0]:roi[1][1]]
		image = morphological_operation(image, el, iterations=iterations)
		# from the contours of the image compute its 
		# moments and from them derive the center if the
		# area falls inside a given range

		# OPENCV 2.4.X
		if '2.4' in cv2.__version__:
			contours = cv2.findContours(
				image,
				cv2.RETR_LIST,
				cv2.CHAIN_APPROX_SIMPLE)
			contours = contours[0]

		# OPENCV 3.X 
		else:
			im, contours, hierarchy = cv2.findContours(
				image,
				cv2.RETR_LIST,
				cv2.CHAIN_APPROX_SIMPLE)

		for contour in contours:
			m = cv2.moments(contour)
			area =  cv2.contourArea(contour)
			if THRESHOLDS[0] < area < THRESHOLDS[1]:
				try:
					center = (int(m['m10']/m['m00']),
					  int(m['m01']/m['m00'])+roi[1][0])
					# Assume first match is the element
					return center
				except:
					pass

	return _find_center


def grid_coordinates(roi, x_divisions, y_divisions, position):
	"""
	Function that returns the grid coordinates of a given position.
	To do so it computes, for a given area and taking into account
	the number of x and y divisions which is the total amount of cells.
	After that it maps the given position to the cell it falls inside and
	returns the coordinates of that cell. Finally, it is assumed that 
	the position is always inside the grid
	:param roi: region of interest to be gridezied
	:param x_divisions:number of divisions in the x axis
	:param y_divisions:number of divisions in the y axis
	:param position: position to transform into grid coordinates 
	"""
	px_per_x_division = float(roi[0][1]-roi[0][0])/x_divisions
	px_per_y_division = float(roi[1][1]-roi[1][0])/y_divisions
	x_in_grid = position[0] - roi[0][0]
	y_in_grid = position[1] - roi[1][0]
	return (int(x_in_grid/px_per_x_division), int(y_in_grid/px_per_y_division))


def _draw_grid(image, roi, x_divisions, y_divisions):
	"""
	Helper function that draws a grid in an image. To do so it needs
	the initial and final (x, y) coordinates of the grid with respect 
	to the image and the number of divisions.
	:param image: np.array with the image where the grid is to be drawn
	:param roi: initial and final coordinates of the region that covers
	the grid with respect to the image
	:param x_divisions: number of divisions in the x axis
	:param y_divisions: number of divisions in the y axis
	:return image_with_grid: np.array of the image with the grid drawn
	"""
	px_per_x_division = float(roi[0][1]-roi[0][0])/x_divisions
	px_per_y_division = float(roi[1][1]-roi[1][0])/y_divisions
	for x_cell in range(x_divisions+1):
		cv2.line(image, (roi[0][0]+int(x_cell*px_per_x_division), roi[1][0]),
					    (roi[0][0]+int(x_cell*px_per_x_division), roi[1][1]),
					    (0,255,0), 1)
	for y_cell in range(x_divisions+1):
		cv2.line(image, (roi[0][0], roi[1][0]+int(y_cell*px_per_y_division)),
					    (roi[0][1], roi[1][0]+int(y_cell*px_per_y_division)),
					    (0,255,0), 1)
	return image

def get_score(frame):
	"""
	Function that extracts the current game score from a frame via tesseract ocr

	:param frame: np.array with current frame of the game where the score is to be extracted
	:returns score: int with the current score of the game or empty string
	"""
	# Focus first on the area where the fail message is and build a PIL image from the numpy array
	fail_area = frame[FAIL_ROI[1][0]:FAIL_ROI[1][1], FAIL_ROI[0][0]:FAIL_ROI[1][1]]
	fail_im = Image.fromarray(fail_area.astype('uint8'), 'RGB')
	# First check, by the color of the number, if the robot failed the throw
	fail_message = ps.image_to_string(fail_im)
	if fail_message:
		return -1
	# Focus only on the area where the score is and build a PIL image from the numpy array
	numb_area = frame[NUMBERS_ROI[1][0]:NUMBERS_ROI[1][1], NUMBERS_ROI[0][0]:NUMBERS_ROI[1][1]]
	im = Image.fromarray(numb_area.astype('uint8'), 'RGB')
	# Specify that the image should be treated as only containing
	# one word (config param) and extract current score 
	current_score = ps.image_to_string(im, config='-psm 8')
	# retrieve numbers in order
	current_score = ''.join([i for i in current_score if i in NUMBERS])
	if current_score:
		try:
			current_score = int(current_score)
		except ValueError:
			current_score = None
	else:
		current_score = None

	return current_score


if __name__ == "__main__":
	# This tests the functions defined above
	cur_path = os.path.abspath(__file__)
	# If calling game_state.py from another dir that is not cv this will not work
	video_path = os.path.relpath('resources/playthrough_3.mp4', cur_path)
	screen_view = False
	only_get_score = False
	processor = process_video(video_path, screen_view) 
	frames = processor.next()
	while True:
		frames = processor.send(only_get_score)
		if frames:
			if only_get_score:
				print frames
			else:
				print frames[-1] # current score
				print frames[-2], frames[-3]
			if screen_view:
				bin_gray = cv2.cvtColor(frames[0], cv2.COLOR_GRAY2BGR)
				frames = np.hstack((frames[1],bin_gray))
				cv2.imshow('frame', frames)
		#time.sleep(0.03) # slow down so that the human eye can appreciate it
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break