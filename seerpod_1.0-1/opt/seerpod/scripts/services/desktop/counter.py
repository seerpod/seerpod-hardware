from SimpleCV import cv2, Image
import argparse
import sys
import logging
import config
from back_subtractor import BackgroundSubtractor
from tracker import Tracker

class Counter(object):
	capture = None

	def __init__(self):
		print "vs:" + str(config.videoSource)
		self.capture = cv2.VideoCapture(config.videoSource)

	def start(self):
		if not(self.capture.isOpened()):
			print str(self.capture)
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
	parser.add_argument("-out", "--outFile", default="out/counts.out", help="output file path")
	parser.add_argument("-cat", "--contourAreaThresh", default=40000, help="min area of contours to pass human test")
	parser.add_argument("-ll", "--logLevel", default="debug", help="log level [info/debug/warn/error/critical]")
	parser.add_argument("-lf", "--logFile", default="logs/seerpod-rotating.log", help="log file path")

	return parser.parse_args()

if __name__ == "__main__":
	args = parseArguments()
	config.init(args)
	counter = Counter()

	counter.start()
	if config.logger.isEnabledFor(logging.INFO):
		config.logger.info("Counter started")
	
	# initialize a background subtractor (can be one of "absdiff", "simple", or "mog2")
	backSubtrType = "mog2"
	backgroundSubtractor = BackgroundSubtractor(backSubtrType, counter)
	if config.logger.isEnabledFor(logging.DEBUG):
		config.logger.debug("Initialized %s background subtractor", backSubtrType)
	
	# keep on tracking until consecutive 100 exceptions are encountered
	errorCount = 0
	while True:
		trackerType = "single"
		tracker = Tracker(trackerType, backgroundSubtractor)
		if config.logger.isEnabledFor(logging.DEBUG):
			config.logger.debug("Initialized %s tracker", trackerType)

		try:
			return_code = tracker.track(counter)

			if config.logger.isEnabledFor(logging.DEBUG):
				config.logger.debug("Tracker returned code [%s]", return_code)

			if return_code is config.NO_MORE_FRAMES:
				if config.logger.isEnabledFor(logging.INFO):
					config.logger.info("No more frames to analyze. Exiting.")
				sys.exit()

		except Exception as e:
			if config.logger.isEnabledFor(logging.WARN):
				config.logger.warn("Encountered exception in tracking: %s", e)
			errorCount += 1
			if errorCount > 100:
				if config.logger.isEnabledFor(logging.ERROR):
					config.logger.exception("Encountered 100 consecutive exceptions. Exiting.")
				break
	 		continue
	 	errorCount = 0
