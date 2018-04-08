import numpy as np
import cv2
from matplotlib import pyplot as plt


class ClassicMatcher:

	def __init__(self,image1 = None,image2 = None):
		print 'matcher initialized'
		self.left = image1
		self.right = image2

	def matchPoints(self):
		if (self.left is None or self.right is None):
			print 'Images not set'
			return

		gray_left = cv2.cvtColor(self.left,cv2.COLOR_BGR2GRAY)
		gray_right = cv2.cvtColor(self.right,cv2.COLOR_BGR2GRAY)

		self.borders_left = cv2.Canny(gray_left,100,200)
		self.borders_right = cv2.Canny(gray_right,100,200)

		height, width = self.borders_left.shape

		for row in range(5,height-5):
			for column in range(5,width-5):
				if(self.borders_left[row][column] == 255):
					self.borders_left[row][column] = 125
					patch_left = self.getImagePatch(self.left,row,column)

				if(row == 5) or (row == height-6) or (column == 5) or (column == width-6):
					self.borders_left[row][column] = 255 




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

	def getImagePatch(self,image,position_x,position_y,size = 3):
		#print 'getImagePatch'
		return image[position_x-size:position_x+size,position_y-size:position_y+size]

	def getError(self):
		print 'getError'
