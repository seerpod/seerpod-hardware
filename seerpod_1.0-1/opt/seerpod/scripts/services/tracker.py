from SimpleCV import *
import logging
import config
import contour as ctour

class Tracker:
	tracker = None
	backgroundSubtr = None

	def __init__(self, type, backgroundSubtr):
		self.type = type
		if type is "single":
			self.tracker = SingleObjectTracker(backgroundSubtr)
		elif type is "multiple":
			self.tracker = MultipleObjectTracker(backgroundSubtr)

	def track(self, counter):
		self.tracker.track(counter)

	def isSubjectOutOfFrame(self, featureSet):
		if featureSet != []:
			# featureSet is not empty
			if featureSet[-1].getBB()[0] == 0 and featureSet[-1].getBB()[1] == 0 and \
				featureSet[-1].getBB()[2] == 0 and featureSet[-1].getBB()[3] == 0:
				return True
			else:
				return False
		return False

class SingleObjectTracker(Tracker):
	def __init__(self, backgroundSubtr):
		self.backgroundSubtr = backgroundSubtr

	def track(self, counter):
		inCount = 0
		outCount = 0
		
		globalCount = 0
		fs_list = []
		while True:
			human_ctour_img, human_ctours = ctour.getHumanContours(counter, 
												self.backgroundSubtr) # Get Bounding Box

			if human_ctour_img is None:
				if config.logger.isEnabledFor(logging.DEBUG):
					config.logger.debug("No more frames to analyze, exiting")
				return config.NO_MORE_FRAMES

			h, w = human_ctour_img.shape[:2]

			img = counter.convertToSimpleCvImage(human_ctour_img)
			fs_list.append([])
			fs1 = fs_list[globalCount]
			yCoord = []
			count = 0
			trackingStarted = 0
			movingIn = False
			movingOut = False

			# choose only one contour from human_ctours
			target_ctour = None
			for key in human_ctours:
				target_ctour = human_ctours[key]
				break

			for raspi_frame in counter.camera.capture_continuous(counter.capture, format="bgr", use_video_port=True):
				opencv_img = raspi_frame.array
				# clear the stream in preparation for the next frame
				counter.capture.truncate(0)

				fg_mask = self.backgroundSubtr.getForegroundMask(opencv_img)
				processed_image,_ = ctour.removeSmallContours(opencv_img, fg_mask, config.contourAreaThresh/2)
				simplecv_img = counter.convertToSimpleCvImage(processed_image)

				# if config.logger.isEnabledFor(logging.DEBUG):
				# 	config.logger.debug("fs1 before track: %s", fs1)
				if config.logger.isEnabledFor(logging.DEBUG):
					config.logger.debug("target_ctour before track: %s", target_ctour)
				if self.isSubjectOutOfFrame(fs1):
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("tracked object out of frame, searching new big contour.")
					break
				try:
					fs1 = simplecv_img.track("camshift", fs1,img, target_ctour, num_frames=5)
				except Exception as e:
					if config.logger.isEnabledFor(logging.WARN):
						config.logger.warn("Encountered exception: %s", e)
					break

				if self.isSubjectOutOfFrame(fs1):
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("tracked object out of frame, searching new big contour.")
					break

				fs1.drawBB(color=Color.RED)
				fs1.showCoordinates()

				# draw the test lines and display counts
				lineLayer = DrawingLayer((w, h))
				lineLayer.line((0, h*config.startTrackingLine),(w, h*config.startTrackingLine),(255,0,0),2)
				lineLayer.line((0, h*config.endTrackingLine),(w, h*config.endTrackingLine),(0,255,0),2)
				lineLayer.line((0, h*(1-config.endTrackingLine)),(w, h*(1-config.endTrackingLine)),(0,0,255),2)
				simplecv_img.addDrawingLayer(lineLayer)
				simplecv_img.applyLayers()
				simplecv_img.dl().selectFont('purisa')
				simplecv_img.drawText("in: " + str(inCount) + "    out: " + str(outCount), x=100, y=30, fontsize=30)

				if config.logger.isEnabledFor(logging.DEBUG):
					config.logger.debug("fs1=%s", fs1[-1].getBB())
				y = fs1[-1].getBB()[1] # from top left (it should go down to 0)
				lengthBB = fs1[-1].getBB()[2]

				simplecv_img.show()

				yCoord.append(y)
				if trackingStarted == 0:
					if (count < config.minFrameToWait):
						# if top most point of the subject is before the startTrackingLine (middle one)
						if (max(yCoord) > (h * config.startTrackingLine)):
							movingIn = True
						# if bottom most point of the subject is after startTrackingLine
						elif (min(yCoord) + lengthBB) < (h * config.startTrackingLine):
							movingOut = True
						# the y coordinate of the detected object has been beyond the central line at least once
						# start tracking and see if it crosses h/6
						if config.logger.isEnabledFor(logging.DEBUG):
							config.logger.debug("started tracking")
						trackingStarted = 1
					elif (count > config.minFrameToWait):
						# tracking hasn't started yet (subject is beyond the startTrack line)
						if config.logger.isEnabledFor(logging.DEBUG):
							config.logger.debug("tracking not started even after %s frames, finding next big contour.", 
								str(config.minFrameToWait))
						break
				elif (trackingStarted == 1) and (count <= config.maxFramesToAnalyze):
					if config.logger.isEnabledFor(logging.DEBUG):
							config.logger.debug("tracking in progress")
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("min yCoord: %s", str(min(yCoord)))
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("max yCoord: %s", str(max(yCoord)))
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("y: %s", y)
					# tracking in progress
					if (min(yCoord) < (h * config.endTrackingLine)) and movingIn:
						if config.logger.isEnabledFor(logging.DEBUG):
							config.logger.debug("subject crossed endTrackingLine while moving in")
						inCount += 1
						movingIn = False
						break
					# check if the lower most point in the bounding box has crossed the lower endTrackingLine
					elif ((max(yCoord) + fs1[-1].getBB()[3]) > (h * (1 - config.endTrackingLine))) and movingOut:
						if config.logger.isEnabledFor(logging.DEBUG):
							config.logger.debug("subject crossed endTrackingLine while moving out")
						outCount += 1
						movingOut = False
						break
				elif count > config.maxFramesToAnalyze:
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("count exceeded maxFramesToAnalyze")
					# subject hasn't crossed h/6 in maxFramesToAnalyze frames; exit loop
					break
				count += 1
			config.out.info("%s|%s", inCount, outCount)
			if config.logger.isEnabledFor(logging.INFO):
				config.logger.info("inCount=%s|outCount=%s", inCount, outCount)
			globalCount += 1

class MultipleObjectTracker(Tracker):
	def __init__(self, backgroundSubtr):
		self.backgroundSubtr = backgroundSubtr

	def track(self, counter):
		# not implemeted yet
		return None
