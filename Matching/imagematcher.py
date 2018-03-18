import numpy as np
import cv2
from matplotlib import pyplot as plt


class ClassicMatcher:

	def __init__(self):
		print 'matcher initialized'

	def matchPoints(self):
		gray_left = cv2.cvtColor(self.left,cv2.COLOR_BGR2GRAY)
		gray_right = cv2.cvtColor(self.right,cv2.COLOR_BGR2GRAY)

		self.borders_left = cv2.Canny(gray_left,100,200)
		self.borders_right = cv2.Canny(gray_right,100,200)



	#Helpers
	def setImages(self,image1,image2):
		self.left = image1
		self.right = image2

	def showImages(self):
		result = np.concatenate((self.borders_left,self.borders_right),1)
		cv2.namedWindow('result',cv2.WINDOW_NORMAL)
		cv2.resizeWindow('result',1300,600)
		cv2.imshow('result',result)
		cv2.waitKey(0)

