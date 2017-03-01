import matplotlib.pyplot as plt
from pipeline_solution import *
from scipy import misc
from moviepy.editor import VideoFileClip

INPUT_VIDEO = "videos/clip1.mp4"
#INPUT_VIDEO = "videos/clip2.mp4"
#INPUT_VIDEO = "videos/solidWhiteRight.mp4"
#INPUT_VIDEO = "videos/solidYellowLeft.mp4"
OUTPUT_VIDEO = "out1.mp4"

INPUT_IMAGE = "images/img1.png"
#INPUT_IMAGE = "images/img2.png"
#INPUT_IMAGE = "images/solidWhiteCurve.jpg"
#INPUT_IMAGE = "images/solidWhiteRight.jpg"
#INPUT_IMAGE = "images/solidYellowCurve2.jpg"

def img_test():
	img = misc.imread(INPUT_IMAGE)
	plt.imshow(pipeline(img))
	plt.show()

def video_test():
	clip = VideoFileClip(INPUT_VIDEO) #.subclip(5,10)
	transformed = clip.fl_image(pipeline)
	transformed.write_videofile(OUTPUT_VIDEO, audio=False)


img_test()
#video_test()