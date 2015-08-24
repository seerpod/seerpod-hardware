from SimpleCV import np, cv2
import logging
import sys
import config

# Returns the bounding box of the contour which has area > contourAreaThresh
def getBigContours(counter, bkgSubtr):
	if config.logger.isEnabledFor(logging.DEBUG):
		config.logger.debug("Finding foreground object..."),

	while(1):
		# print ".",
		# sys.stdout.flush()
		frame = counter.getNextFrame()

		if frame is None:
			if config.logger.isEnabledFor(logging.DEBUG):
				config.logger.debug("No more frames to analyze, exiting")
			sys.exit()

		height, width  = frame.shape[:2]
		frameArea = width * height

		# apply background subtraction
		fgmask = bkgSubtr.getForegroundMask(frame)

		# initialize a mask of all 255s which will be used in removing small contours
		mask = np.ones(frame.shape[:2], dtype="uint8") * 255

		contours, hier = cv2.findContours(fgmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

		# find contour with area > contourThreshArea
		contourFound = 0
		boundingBoxes = {}
		for cnt in contours:
			ctourArea = cv2.contourArea(cnt)
			if config.contourAreaThresh < ctourArea < (0.7 * frameArea):
				if config.logger.isEnabledFor(logging.DEBUG):
					config.logger.debug("Passing contour area: %s", ctourArea)
				(x,y,w,h) = cv2.boundingRect(cnt)
				if config.logger.isEnabledFor(logging.DEBUG):
					config.logger.debug("bb: %s", (x,y,w,h))
				newX = x + int(w * config.bbRatio)
				newY = y + int(h * config.bbRatio)
				newXmax = newX + int(w * config.bbRatio)
				newYmax = newY + int(h * config.bbRatio)
				key = str(newX) + "|" + str(newY) + "|" + str(newXmax - newX) + "|" + str(newYmax - newY)
				boundingBoxes[key] = (newX, newY, newXmax - newX, newYmax - newY)
				if config.logger.isEnabledFor(logging.DEBUG):
					config.logger.debug("new bb: %s", (newX, newY, newXmax - newX, newYmax - newY))
				contourFound = 1
			else: # mask the unwanted contours
				cv2.drawContours(mask, [cnt], -1, 0, -1)
		
		if contourFound == 1:
			# apply fgmask on original image to extract foreground
			orig_masked = cv2.bitwise_and(frame, frame, mask=fgmask)
			# apply mask on orig_masked to hide small contours
			orig_masked = cv2.bitwise_and(orig_masked, orig_masked, mask=mask)
			# apply median blur to smoothen the image
			orig_masked = cv2.medianBlur(orig_masked, 5)
			
			# all the coordinates are assuming top left corner as origin (0,0) and lower area positive
			# cv2.circle(orig_masked,(x,y), 10, (0,255,0), -1)
			# cv2.circle(orig_masked,(newX,newY), 10, (0,0,255), -1)
			# cv2.rectangle(orig_masked,(x, y),(x+w, y+h),(0,255,0),3)
			# cv2.rectangle(orig_masked,(newX, newY),(newXmax, newYmax),(255,0,0),3)
			return (orig_masked, boundingBoxes)

	# target contour not found in the video
	if config.logger.isEnabledFor(logging.DEBUG):
		config.logger.debug("no contour with area > contourAreaThresh found")
	return (None, None)

def removeSmallContours(orig_image, fgmask, minContourArea):
	# initialize a mask of all 255s which will be used in removing small contours
	mask = np.ones(orig_image.shape[:2], dtype="uint8") * 255

	contours, hier = cv2.findContours(fgmask,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)

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

	return orig_masked, contours

def findNewBigContours(contours, fsMapForBBs, frameArea):
	bigContours = {}
	for cnt in contours:
		if contourAreaThresh < cv2.contourArea(cnt) < (0.7 * frameArea):
			(x,y,w,h) = cv2.boundingRect(cnt)
			for key in fsMapForBBs:
				(fx, fy, fw, fh) = fsMapForBBs[key][-1].getBB()
				#print "x,y,w,h: " + str(x) + "," + str(y) + "," + str(w) + "," + str(h)
				#print "fx,fy,fw,fh: " + str(fx) + "," + str(fy) + "," + str(fw) + "," + str(fh)
				if (((fx > x) and (fx < (x + w))) or ((x > fx) and (x < (fx + fw)))) \
				   and (((fy > y) and (fy < (y + h))) or ((y > fy) and (y < (fy + fh)))):
					# contours intersect
					if config.logger.isEnabledFor(logging.DEBUG):
						config.logger.debug("contours intersect, not adding to new big contours")
				else:
					# add to new big contours
					newX = x + int(w * config.bbRatio)
					newY = y + int(h * config.bbRatio)
					newXmax = newX + int(w * config.bbRatio)
					newYmax = newY + int(h * config.bbRatio)
					key = str(newX) + "|" + str(newY) + "|" + str(newXmax - newX) + "|" + str(newYmax - newY)
					bigContours[key] = (newX, newY, newXmax - newX, newYmax - newY)


	return bigContours

def getHumanContours(counter, bkgSubtr):
	image, humanContours = getBigContours(counter, bkgSubtr)
	return image, humanContours
