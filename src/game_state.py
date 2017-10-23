import cv2
import numpy as np
# for testing purposes
import time
import os

BALL_AREA_THRES = (0, 1250)
BASKET_AREA_THRES = (700, 1000)
BALL_ROI = ((0, 202), (250, 360))
BASKET_ROI = ((0, 202), (50, 200))
BALL = "ball"
BASKET = "basket"


def process_video(source = 0, screen_view = True):
	"""
	This method is given a video source, reads from it until 
	key "q" is pressed and yields the ball center coordinates.
	It is defined as a generator so that the video processing loop
	can be separated from the rest of the program logic

	param::source:: int/str Video source
	param::screen_view:: bool show what is happening or not
	"""
	cap = cv2.VideoCapture(source)
	find_ball_center = find_center(BALL, 6)
	find_basket_center = find_center(BASKET, 1)

	while(cap.isOpened()):
		ret, frame = cap.read()
		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		_, binarized = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		ball_center  = find_ball_center(binarized, BALL_ROI)
		basket_center = find_basket_center(binarized, BASKET_ROI)

		if screen_view and ball_center is not None :
			for i in ball_center:
				cv2.circle(frame,(i[0],i[1]),2,(0,0,255),3)
			for i in basket_center:
				cv2.circle(frame,(i[0],i[1]),2,(255,0,0),3)

			yield (binarized, frame, ball_center)
			continue

		yield ball_center

	cap.release()
	cv2.destroyAllWindows()

def find_center(element, iterations):
	"""
	Closure that expects an element to search for as input and returns
	a function able to find the center of that element in an image

	param::element:: str "ball"/"basket" that specifies the element to search for
	param::iterations:: int number of times the morphological operation should be performed 
	"""
	# Define morphological operation, structuruing element
	# and threshold depending on what are we looking for
	if element == BASKET:
		el = cv2.getStructuringElement(cv2.MORPH_RECT,(5,5))	
		THRESHOLDS = BASKET_AREA_THRES
		morphological_operation = cv2.erode	
	elif element == BALL:
		el = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5,5))
		THRESHOLDS = BALL_AREA_THRES
		morphological_operation = cv2.dilate

	def _find_center(image, roi):
		"""
		This function, once having defined the required values of the element
		we are looking for, searchs for that element in the region of
		interest and returns its center

		param::image:: np.array() of the binarized image to be processed
		param::roi:: ((x1, x2), (y1, y2))
		"""
		# apply morphological operation to region of interest
		image = image[roi[1][0]:roi[1][1], roi[0][0]:roi[1][1]]
		image = morphological_operation(image, el, iterations=iterations)
		cv2.imshow("dilated", image)
		# from the contours of the image compute its 
		# moments and from them derive the center if the
		# area falls inside a given range
		im, contours, hierarchy = cv2.findContours(
			image,
			cv2.RETR_LIST,
			cv2.CHAIN_APPROX_SIMPLE)

		centers = []
		for contour in contours:
			m = cv2.moments(contour)
			area =  cv2.contourArea(contour)
			if THRESHOLDS[0] < area < THRESHOLDS[1]:
				try:
					center = (int(m['m10']/m['m00']),
					  int(m['m01']/m['m00'])+roi[1][0])
					centers.append(center)
				except:
					pass
		return centers			
	return _find_center

def predict_movement(basket_centers):
	"""
	Given n consecutive basket centers and the time between frames, compute
	the predicted position of the basket for the next frame.
	With two consecutive frames we predict with velocity, with three consecutive
	frames we can also estimate accleration.

	param::basket_centers::((pos_0, time_0), (pos_1, time_1), ..., (pos_n, time_n))
	"""
	pass

if __name__ == "__main__":
	# This test both of the functions defined above
	cur_path = os.path.abspath(__file__)
	video_path = os.path.relpath('resources/playthrough.mp4', cur_path)
	processor = process_video(video_path) 
	while True:
		frames = processor.next()
		bin_gray = cv2.cvtColor(frames[0], cv2.COLOR_GRAY2BGR)
		frames = np.hstack((frames[1],bin_gray))
		cv2.imshow('frame', frames)
		time.sleep(0.01)
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break