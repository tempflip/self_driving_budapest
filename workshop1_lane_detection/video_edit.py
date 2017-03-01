from moviepy.editor import VideoFileClip
import matplotlib.pyplot as plt
from scipy import misc

INPUT_VIDEO = "astoria.mp4"
#OUTPUT_VIDEO = "videos/clip2.mp4"


clip = VideoFileClip(INPUT_VIDEO)

def img_dump(clip, start, step, times):
	for i in range(times):
		t = start + i*step
		f = clip.get_frame(t)
		misc.imsave("images/frame_2_{}.png".format(str(t).zfill(4)), f)

def clip_dump(clip, f, to, output ):
	out_clip = clip.subclip(f, to)
	out_clip.write_videofile(output, audio=False)


#img_dump(clip, 100, 1, 40)
clip_dump(clip, 80, 140, 'videos/clip_long1.mp4')