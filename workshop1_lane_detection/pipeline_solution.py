import numpy as np
import cv2
from math import *
import matplotlib.pyplot as plt

# blur and canny parameters
BLUR_KERNEL_SIZE = 5
CANNY_LOW_THRESHOLD = 50
CANNY_HIGH_THRESHOLD = 150


# the hough transaform parameters
H_RHO = 1 # distance resolution in pixels of the Hough grid
H_THETA = np.pi/90 # angular resolution in radians of the Hough grid
H_THRESHOLD = 15     # minimum number of votes (intersections in Hough grid cell)
H_MIN_LINE_LENGTH = 30 #minimum number of pixels making up a line
H_MAX_LINE_GAP = 100    # maximum gap in pixels between connectable line segments

# mask coordinates
MASK_CUT_Y_TOP = 0.5
MASK_CUT_X_TOP_LEFT = 0.45
MASK_CUT_X_TOP_RIGHT = 0.45
MASK_CUT_X_BOTTOM_LEFT = 0
MASK_CUT_X_BOTTOM_RIGHT = 1

MIN_ABS_LINE_SLOPE = 0.2

LANE_CUT = 0.6

MOVING_AVG_FRAMES = 15

lane_lines_history = []

def get_line_func(x1, y1, x2, y2):
	m = (y2 - y1)  / (x2 - x1)
	b1 = y1 - m * x1
	return m, b1

# calculates the x for a linear function
def get_x(m, b, y):
	if m == inf or b == inf:  return 0
	return int((y-b) / m)

def line_length(x1, y1, x2, y2):
	return sqrt((x1 - x2)**2 + (y1-y2)**2)

# filters the lines returned by the hough transform
# 1, returns lines in a map, grouped by positive/negative slope
# 2, draws the lines on the image
def filter_lines(lines, img):

	img_with_lines = np.array(img)
	line_map = {True  : [], False : []}
	for line in lines:
		for (x1, y1, x2, y2) in line:
			m, b = get_line_func(x1, y1, x2, y2)
			# filtering by slope
			if (abs(m) < MIN_ABS_LINE_SLOPE) : continue

			# grouping the lines by slope
			line_map[m > 0].append((m, b, x1, y1, x2, y2))

	# filtering the outliers
	line_map[False] = filter_m_b_tuples(line_map[False])
	line_map[True] = filter_m_b_tuples(line_map[True])

	#drawing the lines
	for m, b, x1, y1, x2, y2 in line_map[True]:
		cv2.line(img_with_lines, (int(x1), int(y1)), (int(x2), int(y2)), (255,165,0), 2)
	#drawing the lines
	for m, b, x1, y1, x2, y2 in line_map[False]:
		cv2.line(img_with_lines, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 255), 2)





	return line_map, img_with_lines

# filters the outliers from the list of (m, b) list
def filter_m_b_tuples(mb_tuple_list):
	if len(mb_tuple_list) == 0 : return mb_tuple_list

	filtered = np.array(mb_tuple_list)

	mean = np.mean(filtered, axis=0)
	std = np.std(filtered, axis=0)

	top_limit = mean + std * 1
	bottom_limit = mean - std * 1

	filtered = filtered[filtered[:,0] > bottom_limit[0] ]
	filtered = filtered[filtered[:,0] < top_limit[0] ]
	filtered = filtered[filtered[:,1] > bottom_limit[1] ]
	filtered = filtered[filtered[:,1] < top_limit[1] ]

	return [tuple(x) for x in np.asarray(filtered)]


# 1, calculating the avarage lines (post/neg)from the filtered line map, one for each slope direction
# 2, makes a moving-average smoothing
def get_lane_lines(line_map, avg_frames = 1):
	final_slopes = {}

	#calculating the average for the current frame lines
	for direction in line_map:
		# this is when there is no data for the current frame
		# in this case we are getting the last frame slope from the history
		if len(line_map[direction]) == 0:
			final_slopes[direction] = lane_lines_history[-1][direction]
			continue

		m_sum = 0
		b_sum = 0
		for m, b, x1, y2, x2, y2 in line_map[direction]:
			m_sum += m
			b_sum += b
		final_slopes[direction] = (m_sum / len(line_map[direction]), b_sum / len(line_map[direction]))
	
	lane_lines_history.append(final_slopes)

	# calculating the m and b moving avgs both for positive and negative directions
	avg_map = {True : [], False : []}
	for f in lane_lines_history[-avg_frames:]:
		m,b = f[True]
		if m != inf and m != -inf:
			avg_map[True].append(f[True])

		m,b = f[False]
		if m != inf and m != -inf:
			avg_map[False].append(f[False])


	# if there are no candidates (can happen when there is a lot of noise on consecutive frames)
	if len(avg_map[True]) > 0:
		pos_mean = np.mean(np.array(avg_map[True]), axis = 0)
	else:
		pos_mean = (1,0)

	if len(avg_map[False]) > 0:
		neg_mean = np.mean(np.array(avg_map[False]), axis = 0)
	else:
		neg_mean = (1,0)


	return_map = {
		True : (pos_mean[0], pos_mean[1]),
		False : (neg_mean[0], neg_mean[1])
	}



	return return_map

def pipeline(img):
	H = img.shape[0]
	W = img.shape[1]	

	## blur and canny edges
	blur_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	blur_gray = cv2.GaussianBlur(blur_gray, (BLUR_KERNEL_SIZE, BLUR_KERNEL_SIZE), 0)
	edges = cv2.Canny(blur_gray, CANNY_LOW_THRESHOLD, CANNY_HIGH_THRESHOLD)

	## masking
	mask_vertices = np.array([[
		(int(W * MASK_CUT_X_TOP_LEFT), int(H * MASK_CUT_Y_TOP)),
		(int(W * MASK_CUT_X_TOP_RIGHT), int(H * MASK_CUT_Y_TOP)),
		(int(W * MASK_CUT_X_BOTTOM_RIGHT) , int(H)),
		(int(W * MASK_CUT_X_BOTTOM_LEFT), int(H))]])
	mask = np.zeros_like(edges)
	mask = cv2.fillPoly(mask, mask_vertices, 255)
	masked_edges = cv2.bitwise_and(edges, mask)

	## getting the lines with a hough-transform
	lines = cv2.HoughLinesP(masked_edges, H_RHO, H_THETA, H_THRESHOLD, np.array([]),
	                            H_MIN_LINE_LENGTH, H_MAX_LINE_GAP)

	# 2 lists for the lines.
	# grouping them by slope direction (positive / negative)
	line_map, img_with_lines = filter_lines(lines, img)
	
	# drawing the mask vertices on the image
	cv2.line(img_with_lines, tuple(mask_vertices[0,0]), tuple(mask_vertices[0,3]), (0, 0, 200), 2)
	cv2.line(img_with_lines, tuple(mask_vertices[0,1]), tuple(mask_vertices[0,2]), (0, 0, 200), 2)

	## calculating the average slope, for both directions

	# calcutaing the line without moving avg
	final_lines_1 = get_lane_lines(line_map, avg_frames = 1)
	final_image_1 = np.array(img)
	for dir in final_lines_1:
		m, b = final_lines_1[dir]
		cv2.line(final_image_1, (get_x(m, b, int(H * LANE_CUT)), int(H * LANE_CUT)), (get_x(m, b, H), H), (0, 255, 0), 3)

	# calculating the lane, with moving avg
	final_lines_moving = get_lane_lines(line_map, avg_frames = MOVING_AVG_FRAMES)

	m_left, b_left = final_lines_moving[True]
	m_right, b_right = final_lines_moving[False]
	
	lane_cover_coords = np.array([[
		(get_x(m_left, b_left, int(H * LANE_CUT)), int(H * LANE_CUT)),
		(get_x(m_left, b_left, H), H),
		(get_x(m_right, b_right, H), H),
		(get_x(m_right, b_right, int(H * LANE_CUT)), int(H * LANE_CUT)),
	]])

	lane_cover = cv2.fillPoly(np.zeros_like(img), lane_cover_coords, (255, 105, 180))
	final_image_moving = cv2.addWeighted(img, 1, lane_cover, 0.5, 0)
	#cv2.line(final_image_moving, (get_x(m, b, int(H * LANE_CUT)), int(H * LANE_CUT)), (get_x(m, b, H), H), (0, 255, 0), 3)
		


	# putting together the frame

	rgb_masked_edges = np.dstack((masked_edges, masked_edges, masked_edges))

	left = np.concatenate((img_with_lines, rgb_masked_edges), axis = 0 )
	right = np.concatenate((final_image_1, final_image_moving), axis = 0)

	out = np.concatenate((left, right), axis = 1)
	
	return out
