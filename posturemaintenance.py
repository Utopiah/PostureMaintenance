#!/usr/bin/python

# use uvcdynctrl -s 'LED1 Mode' 0 to avoid getting blind by the anoying activity LED

import sys
import cv
import time
import os

# aka Rottenmeyer factor
errorrange = 5 # should becomme a comand-line parameter
badly_seated_message = "time to seat properly !"
well_seated_message = "well seated"
bad_sitting_command = 'ratpoison -c "echo time to seat properly !"'
calibrated_message = "face found, position calibrated"

cam_led_off = "uvcdynctrl -s 'LED1 Mode' 0"
cam_led_on = "uvcdynctrl -s 'LED1 Mode' 1"

haarcascade_file = 'haarcascade_frontalface_default.xml' # current directory

class FaceDetect():
	def __init__(self):
		device = 0
		self.capture = cv.CaptureFromCAM(device)
		capture_size = (320,200)
		# forcing lower resolution
		cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_WIDTH, capture_size[0])
		cv.SetCaptureProperty(self.capture, cv.CV_CAP_PROP_FRAME_HEIGHT, capture_size[1])
		self.calibration = (0, 0)

	def detect(self):
		cv.CvtColor(self.frame, self.grayscale, cv.CV_RGB2GRAY)

		#equalize histogram
		cv.EqualizeHist(self.grayscale, self.grayscale)

		# detect objects
		faces = cv.HaarDetectObjects(image=self.grayscale, cascade=self.cascade, storage=self.storage, scale_factor=1.2,
			min_neighbors=2, flags=cv.CV_HAAR_DO_CANNY_PRUNING)

		if faces:
			for i in faces:
			# should actually solely consider the face closest to the center
				if i[1] > 10:
					now = int(time.time())
					if self.calibration[0] < 1: 
						self.calibration = ((i[0][0]+i[0][2])/2, (i[0][1]+i[0][3])/2)
						os.system(cam_led_off)
						print now, calibrated_message
					# compare current position with calibrated position
					if self.calibration[0] - (i[0][0]+i[0][2])/2 > errorrange:
					# if in the right range, e.g. not too low, not too high (10% percentage of absolute value difference)
						print now, badly_seated_message
						# just kept for debug
						os.system(bad_sitting_command)
						# could keep track of history overall and send more serious warning if above a certain threshold
						# http://synergy-foss.org http://packages.debian.org/sid/libxtst-dev 
					else:
						print now, well_seated_message
						# just kept for debug, pratical to see that the camera is still finding the face

	def run(self):
		# check if capture device is OK
		if not self.capture:
			print "Error opening capture device"
			sys.exit(1)

		self.frame = cv.QueryFrame(self.capture)
		self.image_size = cv.GetSize(self.frame)

		# create grayscale version
		self.grayscale = cv.CreateImage(self.image_size, 8, 1)

		# create storage
		self.storage = cv.CreateMemStorage(128)
		self.cascade = cv.Load(haarcascade_file)

		while 1:
		# do forever
			time.sleep(1)
			# gentle on the CPU
			# eventually could decide so skip more frames if nothing for a long period

			# capture the current frame
			self.frame = cv.QueryFrame(self.capture)
			if self.frame is None:
				break

			# mirror
			cv.Flip(self.frame, None, 1)

			# face detection
			self.detect()
			# XXX never get executed when program is forced to stop
			os.system(cam_led_off)
		sys.exit(1)

if __name__ == "__main__":
	print "hunting for a face to recognize (make sure the light is ok and you are well seated)"
	face_detect = FaceDetect()
	face_detect.run() 
