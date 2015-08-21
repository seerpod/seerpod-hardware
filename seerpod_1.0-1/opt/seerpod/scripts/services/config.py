# Configuration.py
## Defines global variables that are used throughout
## the project

def init():
	#global videoType = "stream"
	global videoType
	videoType = "file"
	
	#global videoSource = "0"
	global videoSource
	videoSource = 'images/Video2-short.mp4'

	global contourAreaThresh
	contourAreaThresh = 5000
	global minFrameToWait
	minFrameToWait = 3
	global maxFramesToAnalyze
	maxFramesToAnalyze = 80
	global startTrackingLine
	startTrackingLine = 1/float(2)
	global endTrackingLine
	endTrackingLine = 1/float(6)
	global bbRatio
	bbRatio = 1/float(3)

	##
	# return codes
	##
	global NO_MORE_FRAMES
	NO_MORE_FRAMES = 0