import logging
import logging.handlers
import os
from rotatingfile import RotatingFile

# config.py
## Defines global variables that are used throughout
## the project

def init(args):
	#global videoType = "file"
	global videoType
	videoType = args.videoType
	
	#global videoSource = 'images/Video2-short.mp4'
	global videoSource
	if videoType == "stream":
		videoSource = int(args.videoSource)
	else:
		videoSource = args.videoSource

	global out
	out = initOutFile(args.outFile)

	global contourAreaThresh
	contourAreaThresh = args.contourAreaThresh
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

	global logFile
	logFile = args.logFile

	global logger
	logger = initLogger()

	if args.logLevel == "info":
		logger.setLevel(logging.INFO)
	elif args.logLevel == "debug":
		logger.setLevel(logging.DEBUG)
	elif args.logLevel == "warn":
		logger.setLevel(logging.WARN)
	elif args.logLevel == "error":
		logger.setLevel(logging.ERROR)

def initOutFile(outFile):
	# check for directory existence
	directory, filename = os.path.split(outFile)
	if not os.path.exists(directory):
		os.makedirs(directory)

	outWriter = logging.getLogger("outWriter")
	formatter = logging.Formatter("%(asctime)s %(message)s")

	# create a rotating file handler which creates 
	# 10 files of ~2MB each (max size of logs = 20MB)
	rotatingFileHandler = logging.handlers.RotatingFileHandler(
              outFile, maxBytes=2000000, backupCount=10)
	rotatingFileHandler.setFormatter(formatter)
	outWriter.addHandler(rotatingFileHandler)
	outWriter.setLevel(logging.INFO)

	return outWriter

def initSuperLogger():
	logger = logging.getLogger("rootLogger")
	formatter = logging.Formatter("%(asctime)s "
		"%(levelname)-5.5s [%(module)s:%(funcName)s:%(lineno)d] "
		"%(message)s")

	consoleHandler = logging.StreamHandler()
	consoleHandler.setFormatter(formatter)
	logger.addHandler(consoleHandler)

	# create a rotating file handler which creates 
	# 10 files of ~5MB each (max size of logs = 50MB)
	fileHandler = logging.handlers.RotatingFileHandler(
              logFile, maxBytes=5000000, backupCount=10)
	fileHandler.setFormatter(formatter)
	logger.addHandler(fileHandler)

	return logger

def initLogger():
	genericLogger = initSuperLogger()
	genericLogger.setLevel(logging.DEBUG)
	return genericLogger