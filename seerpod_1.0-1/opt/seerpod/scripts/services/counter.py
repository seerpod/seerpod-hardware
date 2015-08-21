from SimpleCV import cv2, Image
import argparse
import sys
import config
from back_subtractor import BackgroundSubtractor
from tracker import Tracker

class Counter(object):
	capture = None

	def __init__(self):
		self.capture = cv2.VideoCapture(config.videoSource)

	def start(self):
		if not(self.capture.isOpened()):
			self.capture.open()

	def stop(self):
		# close capture stream
		return

	def pause(self):
		# figure out a way to pause the capture stream
		return

	def getNextFrame(self):
		_, frame = self.capture.read()
		return frame

	def getNextSimpleCvImage(self):
		_, frame = self.capture.read()
		simplecvImg = Image(frame.transpose(1,0,2)[:,:,::-1])
		return simplecvImg

	def convertToSimpleCvImage(self, opencvImage):
		return Image(opencvImage.transpose(1,0,2)[:,:,::-1])

def parseArguments():
	parser = argparse.ArgumentParser()
	parser.add_argument("-vt", "--videoType", default="stream", help="video stream or video file [stream/file]")
	parser.add_argument("-vs", "--videoSource", default="0", help="video file path or integer \
		(enclosed on quotes) for video stream")
	parser.add_argument("-cat", "--contourAreaThresh", default=40000, help="min area of contours to pass human test")

	args = parser.parse_args()
	config.videoType = args.videoType
	if config.videoType == "stream":
		config.videoSource = int(args.videoSource)
	else:
		config.videoSource = args.videoSource
	config.contourAreaThresh = args.contourAreaThresh

	# print "config:"
	# print config.videoSource
	# print config.videoType
	# print config.contourAreaThresh
	# print config.minFrameToWait
	# print config.maxFramesToAnalyze
	# print config.startTrackingLine
	# print config.endTrackingLine
	# print config.bbRatio

if __name__ == "__main__":
	config.init()
	parseArguments()
	counter = Counter()

	counter.start()

	# initialize a background subtractor (can be one of "absdiff", "simple", or "mog2")
	backgroundSubtractor = BackgroundSubtractor("mog2", counter)
	
	# keep on tracking indefinitely
	while True:
		#human_ctour_img, humanContours = ctour.getHumanContours(counter, backgroundSubtractor)
		tracker = Tracker("single", backgroundSubtractor)
		try:
			return_code = tracker.track(counter)

			if return_code is config.NO_MORE_FRAMES:
				sys.exit()

		except Exception as e:
			print "Encountered exception in tracking: ", e
	 		continue