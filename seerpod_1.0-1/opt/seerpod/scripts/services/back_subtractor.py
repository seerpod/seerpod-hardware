from SimpleCV import cv2

class BackgroundSubtractor(object):
	subtractor = None
	kernel = None
	background = None
	
	def __init__(self, method, counter):
		if method is "absdiff":
			self.subtractor = AbsDiffSubtractor(counter)
		elif method is "mog2":
			self.subtractor = MOG2Subtractor()
		self.kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

	def getBackground(self):
		return self.subtractor.background

	def getForegroundMask(self, frame):
		return self.subtractor.getForegroundMask(frame)


class AbsDiffSubtractor(BackgroundSubtractor):

	def getBackground(self):
		return self.background

	def __init__(self, counter):
		capture = counter.capture
		count = 0
		# capture frames from the camera
		for frame in counter.camera.capture_continuous(capture, format="bgr", use_video_port=True):
			count += 1
			# grab the raw NumPy array representing the image, then initialize the timestamp
			# and occupied/unoccupied text
			image = frame.array
			bkg = image.copy()
			blurred_bkg = cv2.GaussianBlur(bkg,(3,3),0)

			# clear the stream in preparation for the next frame
			capture.truncate(config.videoSource)
		 	
		 	if (count >= 30):
		 		break
		
		self.background = blurred_bkg

	def getForegroundMask(self, frame):
		imgCopy = frame.copy()
		frame = cv2.GaussianBlur(frame,(3,3),0)
		cv2.absdiff(frame, self.background, imgCopy)
		gray = cv2.cvtColor(imgCopy, cv2.COLOR_BGR2GRAY)
		_, thresh = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
		fgmask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, self.kernel)

		return fgmask


class MOG2Subtractor(BackgroundSubtractor):
	fgbg = None

	def __init__(self):
		self.fgbg = cv2.BackgroundSubtractorMOG2()

	def getForegroundMask(self, frame):
		# apply background subtraction
		fgmask = self.fgbg.apply(frame)

		# apply some filters
		fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)
		ret,fgmask = cv2.threshold(fgmask,127,255,cv2.THRESH_BINARY)
		
		return fgmask