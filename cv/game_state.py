import cv2
import numpy as np
import pytesseract as ps
from PIL import Image
# for testing purposes
import time
import os


BALL_AREA_THRES = (0, 1250)
BASKET_AREA_THRES = (700, 900)
BALL_ROI = ((0, 202), (250, 360))
BASKET_ROI = ((0, 202), (50, 200))
NUMBERS_ROI = ((0, 202), (200, 275))
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

	param::int/str::source Video source
	param::bool::screen_view show what is happening or not
	yields::tuple::(ball_center, basket_center, score) found centers and score or None
	"""
	cap = cv2.VideoCapture(source)
	find_ball_center = find_center(BALL, 6)
	find_basket_center = find_center(BASKET, 1)
	while(cap.isOpened()):
		ret, frame = cap.read()
		measured_time = time.time()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		_, binarized = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		ball_center, basket_center = find_centers(binarized,
												  find_ball_center,
												  find_basket_center)
		if ball_center and basket_center:
			score = get_score(frame)

		if screen_view:
			if ball_center:
				cv2.circle(frame,ball_center,2,(0,0,255),3)
			if basket_center:
				cv2.circle(frame,basket_center,2,(255,0,0),3)
			yield (binarized, frame, ball_center, basket_center, score)
			continue

		yield (ball_center, basket_center, score)
		continue

	cap.release()
	cv2.destroyAllWindows()

def find_centers(binary_img, find_ball_center, find_basket_center):
	"""
	Function that returns both the ball and basket center. If the ball center is
	not found in the ROI it means that the user already shot the ball. Then there
	is no point in estimating the basket center position and hence it is not computed.

	param::np.array::binarized numpy representation of the binarized image
	param::func::find_ball_center function that returns the ball center
	param::func::find_basket_center function that returns the basket center
	returns::tuple::(ball_center, basket_center) coordinates of the centers if found else (None, None)
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

	param::str::element "ball"/"basket" that specifies the element to search for
	param::int::iterations number of times the morphological operation should be performed
	returns::func::find_center function that searchs for the specified element with the
	given parameters 
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

		param::np.array::image of the binarized image to be processed
		returns::tuple::center coordinates of the center of the found element or None
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

def get_score(frame):
	"""
	Function that extracts the current game score from a frame via tesseract ocr

	param::np.array::frame current frame of the game where the score is to be extracted
	returns::int::score current score of the game or empty string
	"""
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
	video_path = os.path.relpath('resources/playthrough.mp4', cur_path)
	processor = process_video(video_path) 
	while True:
		frames = processor.next()
		print frames[-1] # current score
		bin_gray = cv2.cvtColor(frames[0], cv2.COLOR_GRAY2BGR)
		frames = np.hstack((frames[1],bin_gray))
		cv2.imshow('frame', frames)
		#time.sleep(0.03) # slow down so that the human eye can appreciate it
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break