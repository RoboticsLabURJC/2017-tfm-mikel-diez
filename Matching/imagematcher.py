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

		self.gray_left = cv2.cvtColor(self.left,cv2.COLOR_BGR2GRAY)
		self.gray_right = cv2.cvtColor(self.right,cv2.COLOR_BGR2GRAY)

		self.borders_left = cv2.Canny(self.gray_left,100,200)
		self.borders_right = cv2.Canny(self.gray_right,100,200)

		height, width = self.borders_left.shape

		self.result = np.zeros((height,width), np.uint8)

		for row in range(5,height-5):
			print 'row: ' + str(row)
			for column in range(5,width-5):
				if(self.borders_left[row][column] == 255):
					self.borders_left[row][column] = 125
					patch_left = self.getImagePatch(self.gray_left,row,column)
					min_diff = 1000000
					min_x = 0
					min_y = 0
					for right_column in range(5,width-5):
						if(self.borders_right[row][right_column] == 255):
							patch_right = self.getImagePatch(self.gray_right,row,right_column)
							patch_diff = (patch_left - patch_right)**2
							diff_value = np.sum(patch_diff)
							if(diff_value < min_diff):
								min_diff = diff_value
								min_x = row
								min_y = right_column
					if(min_diff < 255):
						self.result[row][right_column] = min_diff
						print 'min_diff: ' + str(min_diff)


				if(row == 5) or (row == height-6) or (column == 5) or (column == width-6):
					self.borders_left[row][column] = 255 




	#Helpers
	def setImages(self,image1,image2):
		self.left = image1
		self.right = image2

	def showImages(self):
		result = np.concatenate((self.borders_left,self.result),1)
		cv2.namedWindow('result',cv2.WINDOW_NORMAL)
		cv2.resizeWindow('result',1300,600)
		cv2.imshow('result',result)
		cv2.waitKey(0)

	def getImagePatch(self,image,position_x,position_y,size = 3):
		#print 'getImagePatch'
		return image[position_x-size:position_x+size,position_y-size:position_y+size]

	def getError(self):
		print 'getError'
