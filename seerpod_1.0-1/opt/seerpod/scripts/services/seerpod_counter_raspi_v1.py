from SimpleCV import *
from picamera.array import PiRGBArray
from picamera import PiCamera
import time
import sys

camera = PiCamera()
camera.resolution = (640, 480)
camera.framerate = 32

contourAreaThresh = 50000
minFrameToWait = 3
maxFramesToAnalyze = 80
startTrackingLine = 1/float(2)
endTrackingLine = 1/float(6)
bbRatio = 1/float(3)

kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))
#fgbg = cv2.BackgroundSubtractorMOG2()

# def getImage(capture):
# 	ret, frame = capture.read()
# 	return frame

# def getSimpleCvImage(opencv_img):
#     simplecvImg = Image(opencv_img.transpose(1,0,2)[:,:,::-1])

#     return simplecvImg

def getBg(rawCapture):
	count = 0
	print("detecting background .")

	# capture frames from the camera
	for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		count += 1
		# grab the raw NumPy array representing the image, then initialize the timestamp
		# and occupied/unoccupied text
		image = frame.array

		bkg=image.copy()
		blurred_bkg = cv2.GaussianBlur(bkg,(3,3),0)

		# clear the stream in preparation for the next frame
		rawCapture.truncate(0)

		print ".",
		sys.stdout.flush()
	 	
	 	if (count >= 30):
	 		break
	
	return blurred_bkg

def extractForegroundMask(image):
	# apply background subtraction
	fgmask = fgbg.apply(image)

	# apply some filters
	fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
	ret,fgmask = cv2.threshold(fgmask,127,255,cv2.THRESH_BINARY)
	
	return fgmask

def extractForegroundMaskAbsDiff(bkg, image):
	copy1 = image.copy()
	image = cv2.GaussianBlur(image,(3,3),0)
	cv2.absdiff(image,bkg,copy1)
	gray = cv2.cvtColor(copy1, cv2.COLOR_BGR2GRAY)
	ret,thresh1 = cv2.threshold(gray,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
	fgmask = cv2.morphologyEx(thresh1, cv2.MORPH_OPEN, kernel)

	return fgmask


def removeSmallContours(orig_image, fgmask, minContourArea):
	# initialize a mask of all 255s which will be used in removing small contours
	mask = np.ones(orig_image.shape[:2], dtype="uint8") * 255

	contours, hier = cv2.findContours(fgmask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

	# find contours with area < minContourArea
	for cnt in contours:
		if cv2.contourArea(cnt) < minContourArea:
			cv2.drawContours(mask, [cnt], -1, 0, -1)

	# apply fgmask on original image to extract foreground
	orig_masked = cv2.bitwise_and(orig_image, orig_image, mask=fgmask)
	# apply mask on orig_masked to hide small contours
	orig_masked = cv2.bitwise_and(orig_masked, orig_masked, mask=mask)
	# apply median blur to smoothen the image
	orig_masked = cv2.medianBlur(orig_masked, 5)

	return orig_masked


# Returns the boundig box of the contour which has area > contourAreaThresh
def getInitialBigContours(bkg, rawCapture):
	print "finding foreground object .",

	#bgimage = getImage(capture)

	for raspi_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
		print ".",
		sys.stdout.flush()

		frame = raspi_frame.array

		# clear the stream in preparation for the next frame
		rawCapture.truncate(0)

		if frame is None:
			print "\nNo more frames to analyze, exiting"
			sys.exit()

		height, width  = frame.shape[:2]
		frameArea = width * height

		# apply background subtraction
		# fgmask = extractForegroundMask(frame)
		fgmask = extractForegroundMaskAbsDiff(bkg, frame)

		# initialize a mask of all 255s which will be used in removing small contours
		mask = np.ones(frame.shape[:2], dtype="uint8") * 255

		contours, hier = cv2.findContours(fgmask,cv2.RETR_LIST,cv2.CHAIN_APPROX_SIMPLE)

		# find contour with area > contourThreshArea
		contourFound = 0
		boundingBoxes = []
		for cnt in contours:
			if contourAreaThresh < cv2.contourArea(cnt) < (0.7 * frameArea):
				print "\npassing contour area: ", cv2.contourArea(cnt)
				(x,y,w,h) = cv2.boundingRect(cnt)
				print "bb: ", (x,y,w,h)
				newX = x + int(w * bbRatio)
				newY = y + int(h * bbRatio)
				newXmax = newX + int(w * bbRatio)
				newYmax = newY + int(h * bbRatio)
				boundingBoxes.append((newX, newY, newXmax - newX, newYmax - newY))
				contourFound = 1
			else:
				cv2.drawContours(mask, [cnt], -1, 0, -1)
		
		if contourFound == 1:
			# apply fgmask on original image to extract foreground
			orig_masked = cv2.bitwise_and(frame, frame, mask=fgmask)
			# apply mask on orig_masked to hide small contours
			orig_masked = cv2.bitwise_and(orig_masked, orig_masked, mask=mask)
			# apply median blur to smoothen the image
			orig_masked = cv2.medianBlur(orig_masked, 5)
			
			print "new bb: ", (newX, newY, newXmax - newX, newYmax - newY)
			# all the coordinates are assuming top left corner as origin (0,0) and lower area positive
			# cv2.circle(orig_masked,(x,y), 10, (0,255,0), -1)
			# cv2.circle(orig_masked,(newX,newY), 10, (0,0,255), -1)
			# cv2.rectangle(orig_masked,(x, y),(x+w, y+h),(0,255,0),3)
			# cv2.rectangle(orig_masked,(newX, newY),(newXmax, newYmax),(255,0,0),3)
			# cv2.imshow("img", orig_masked)
			# time.sleep(10000)

			return (orig_masked, (newX, newY, newXmax - newX, newYmax - newY))

	# target contour not found in the video
	print "no contour with area > contourAreaThresh found"

	return (None, None)

def isSubjectOutOfFrame(featureSet):
	if featureSet != []:
		# featureSet is not empty
		if featureSet[-1].getBB()[0] == 0 and featureSet[-1].getBB()[1] == 0 and \
			featureSet[-1].getBB()[2] == 0 and featureSet[-1].getBB()[3] == 0:
			return True
		else:
			return False
	return False

def camshift(bkg, rawCapture):
	inCount = 0
	outCount = 0
	
	globalCount = 0
	fs_list = []
	while True:
		orig_img, bb1 = getInitialBigContours(bkg, rawCapture) # Get Bounding Boxes

		if orig_img is None:
			print "\nNo more frames to analyze, exiting"
			sys.exit()

		h, w = orig_img.shape[:2]
		# print "minFrameToWait", minFrameToWait
		# print "maxFramesToAnalyze", maxFramesToAnalyze
		# print "startTrackingLine", startTrackingLine
		# print "endTrackingLine", endTrackingLine
		# print "size: ", h, w
		# print "h/6 = ", (h * endTrackingLine)

		#img = Image(orig_img, cv2image=True)
		img = Image(orig_img.transpose(1,0,2)[:,:,::-1])
		fs_list.append([])
		fs1 = fs_list[globalCount]
		yCoord = []
		count = 0
		trackingStarted = 0
		movingIn = False
		movingOut = False
		for raspi_frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
			opencv_img = raspi_frame.array

			# clear the stream in preparation for the next frame
			rawCapture.truncate(0)

			fg_mask = extractForegroundMaskAbsDiff(bkg, opencv_img)
			processed_image = removeSmallContours(opencv_img, fg_mask, contourAreaThresh/2)
			simplecv_img = Image(processed_image.transpose(1,0,2)[:,:,::-1])

			print "fs1 before track: ", fs1
			print "bb1 before track: ", bb1
			if isSubjectOutOfFrame(fs1):
				print "tracked object out of frame, searching new big contour."
				break

			try:
				fs1 = simplecv_img.track("camshift",fs1,img,bb1,num_frames=10)
			except Exception as e:
				print "Encountered exception: ", e
				break
			
			if isSubjectOutOfFrame(fs1):
				print "tracked object out of frame, searching new big contour."
				break

			fs1.drawBB(color=Color.RED)
			fs1.showCoordinates()

			# draw the test lines and display counts
			lineLayer = DrawingLayer((w, h))
			lineLayer.line((0, h*startTrackingLine),(w, h*startTrackingLine),(255,0,0),2)
			lineLayer.line((0, h*endTrackingLine),(w, h*endTrackingLine),(0,255,0),2)
			lineLayer.line((0, h*(1-endTrackingLine)),(w, h*(1-endTrackingLine)),(0,0,255),2)
			simplecv_img.addDrawingLayer(lineLayer)
			simplecv_img.applyLayers()
			simplecv_img.dl().selectFont('purisa')
			simplecv_img.drawText("in: " + str(inCount) + "    out: " + str(outCount), x=100, y=30, fontsize=30)

			print "fs1=", fs1[-1].getBB()
			y = fs1[-1].getBB()[1] # from top left (it should go down to 0)
			lengthBB = fs1[-1].getBB()[2]

			simplecv_img.show()

			# cv2.circle(processed_image,(fs1[-1].getBB()[0],y), 10, (0,255,0), -1)
			# cv2.circle(processed_image,(fs1[-1].getBB()[0],y + lengthBB), 10, (0,255,0), -1)
			# cv2.imshow("img", processed_image)
			# time.sleep(10000)

			yCoord.append(y)
			if trackingStarted == 0:
				print "in tracking started = 0"
				if (count < minFrameToWait):
					# if top most point of the subject is before the startTrackingLine (middle one)
					if (max(yCoord) > (h * startTrackingLine)):
						movingIn = True
					# if bottom most point of the subject is after startTrackingLine
					elif (min(yCoord) + lengthBB) < (h * startTrackingLine):
						movingOut = True
					# the y coordinate of the detected object has been beyond the central line at least once
					# start tracking and see if it crosses h/6
					print "started tracking"
					trackingStarted = 1
				elif (count > minFrameToWait):
					# tracking hasn't started yet (subject is beyond the startTrack line)
					print "tracking not started even after " + str(minFrameToWait) + " frames, finding next big contour."
					break
			elif (trackingStarted == 1) and (count <= maxFramesToAnalyze):
				print "tracking in progress"
				print "min yCoord: ", min(yCoord)
				print "max yCoord: ", max(yCoord)
				print "y: ", y
				# tracking in progress
				if (min(yCoord) < (h * endTrackingLine)) and movingIn:
					print "subject crossed endTrackingLine while moving in"
					inCount += 1
					movingIn = False
					break
				# check if the lower most point in the bounding box has crossed the lower endTrackingLine
				elif ((max(yCoord) + fs1[-1].getBB()[3]) > (h * (1 - endTrackingLine))) and movingOut:
					print "subject crossed endTrackingLine while moving out"
					outCount += 1
					movingOut = False
					break
			elif count > maxFramesToAnalyze:
				print "count exceeded maxFramesToAnalyze"
				# subject hasn't crossed h/6 in maxFramesToAnalyze frames; exit loop
				break
			count += 1
			# fs1.drawBB(color=Color.RED)
			# fs1.showCoordinates()
			# img1.show()
	  		# fs1.drawPath()
	        #fs1.showSizeRatio()
	        #fs1.showPixelVelocity()
	        #fs1.showPixelVelocityRT()
	        #img1.save(d)
		print "inCount: ", inCount
		print "outCount: ", outCount
		globalCount += 1


############# MAIN #################

# initialize the camera and grab a reference to the raw camera capture
rawCapture = PiRGBArray(camera, size=(640, 480))
 
# allow the camera to warmup
time.sleep(0.1)

#cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture('../images/Video2-short.mp4')
#if not(cap.isOpened()):
#    cap.open()
bkg = getBg(rawCapture)
camshift(bkg, rawCapture)