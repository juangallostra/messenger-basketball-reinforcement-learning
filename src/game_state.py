import cv2
import numpy as np
# for testing purposes
import time
import os

BALL_AREA_THRES = (0, 1250)
BASKET_AREA_THRES = (700, 900)
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

	param::source::int/str Video source
	param::screen_view::bool show what is happening or not
	"""
	cap = cv2.VideoCapture(source)
	find_ball_center = find_center(BALL, 6)
	find_basket_center = find_center(BASKET, 1)
	centers_buffer = [None]
	predicted_pos = ()

	while(cap.isOpened()):
		ret, frame = cap.read()
		measured_time = time.time()

		gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		_, binarized = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		ball_center, basket_center = find_centers(binarized,
												  find_ball_center,
												  find_basket_center)
		centers_buffer = update_buffer(centers_buffer, basket_center, measured_time)

		if screen_view:
			if ball_center:
				cv2.circle(frame,ball_center,2,(0,0,255),3)
			if basket_center:
				cv2.circle(frame,basket_center,2,(255,0,0),3)
			if predicted_pos:
				cv2.circle(frame,predicted_pos,2,(0,255,0),3)
			predicted_pos = predict_movement(centers_buffer, 1)
			yield (binarized, frame, ball_center, basket_center, predicted_pos)
			continue

		predicted_pos = predict_movement(centers_buffer, 1)
		yield (ball_center, basket_center, predicted_pos)
		continue

	cap.release()
	cv2.destroyAllWindows()

def find_centers(binary_im, find_ball_center, find_basket_center):
	"""
	Function that returns both the ball and basket center. If the ball center is
	not found in the ROI it means that the user already shot the ball. Then there
	is no point in estimating the basket center position and hence it is not computed.

	param::binarized::np.array of the binarized image
	param::find_ball_center::func function that returns the ball center
	param::find_basket_center::func function that returns the basket center
	"""
	ball_center  = find_ball_center(binary_im)
	# basket center should return only the true center
	# only perform basket detection if ball has been previously found in ROI. 
	if ball_center:
		basket_center = find_basket_center(binary_im)
		return (ball_center, basket_center)
	else:
		return (None, None)


def find_center(element, iterations):
	"""
	Closure that expects an element to search for as input and returns
	a function able to find the center of that element in an image

	param::element::str "ball"/"basket" that specifies the element to search for
	param::iterations::int number of times the morphological operation should be performed 
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

		param::image::np.array of the binarized image to be processed
		param::roi::tuple in the form ((x1, x2), (y1, y2))
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

def predict_movement(basket_centers, steps=1):
	"""
	Given n consecutive basket centers and the time between frames, compute
	the predicted position of the basket for the next number of steps.
	With two consecutive frames we predict with velocity, with three consecutive
	frames we can also estimate accleration.

	param::basket_centers::tuple in the form ((pos_0, time_0), (pos_1, time_1), ..., (pos_n, time_n))
	param::steps::int number of steps into which the position is predicted
	"""
	if len(basket_centers)<=1:
		# Empty prediction (empty buffer)
		return None
	elif len(basket_centers)==2 and None not in basket_centers:
		# predict with speed (up to now this only implements one step prediction)
		pos_0 = basket_centers[0][0]
		pos_1 = basket_centers[1][0]
		delta_t = basket_centers[1][1]-basket_centers[0][1]
		speed = (float(pos_1[0]-pos_0[0])/delta_t, float(pos_1[1]-pos_0[1])/delta_t)
		# Assuming constant frame rate (delta_t should be constant) the predicted position
		# for the next frame is x=x_1+v_x*delta_t & y=y_1+v_y*delta_t
		# Obviously this won't work when bouncing
		return (pos_1[0]+int(speed[0]*delta_t), pos_1[1]+int(speed[1]*delta_t))
	elif len(basket_centers)>2:
		# predict with acceleration and speed
		pass
	# The idea is to be able to predict the position of the basket by measuring its
	# position at different frames

	return None

def update_buffer(centers_buffer, center, measured_time):
	"""
	Updates the buffer that stores the computed positions of the basket_centers. This function
	should be modified if predict_movement is updated.

	param::centers_buffer::tuple/list cotaining centers in the form (x0, y0), ..., (xn-1, yn-1)
	param::centers::tuple  (xn, yn) current center position
	"""
	if not center:
		# if failed to detect the center empty buffer to avoid problems
		return [None]
	elif len(centers_buffer) == 2:
		# update buffer
		centers_buffer.pop(0)
		centers_buffer.append((center, measured_time))
	else:
		centers_buffer.append((center, measured_time))
	return centers_buffer



if __name__ == "__main__":
	# This tests the functions defined above
	cur_path = os.path.abspath(__file__)
	video_path = os.path.relpath('resources/playthrough.mp4', cur_path)
	processor = process_video(video_path) 
	while True:
		frames = processor.next()
		#prediction = predict_movement(centers[1], 1)
		bin_gray = cv2.cvtColor(frames[0], cv2.COLOR_GRAY2BGR)
		frames = np.hstack((frames[1],bin_gray))
		cv2.imshow('frame', frames)
		time.sleep(0.01) # slow down so that the human eye can appreciate it
		if cv2.waitKey(1) & 0xFF == ord('q'):
			break