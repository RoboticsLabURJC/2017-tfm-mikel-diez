import numpy as np
import cv2
import jderobot
import os
import yaml
from matplotlib import pyplot as plt
from Modules.GUI.Helpers import imShowTwoImages, drawlines

class ClassicMatcher:

	def __init__(self,image1 = None,image2 = None):
		print 'matcher initialized'
		self.left = image1
		self.right = image2

	def matchPoints(self):

		height, width = self.borders_left.shape

		self.result = np.zeros((height,width), np.uint8)
		self.matchedPoints = []

		for row in range(5,height-5):
			for column in range(5,width-5):
				if(self.borders_left[row][column] == 255):
					self.borders_left[row][column] = 125
					patch_left = self.getImagePatch(self.left,row,column)
					min_diff = 1000000
					min_x = 0
					min_y = 0
					for right_column in range(5,width-5):
						if(self.borders_right[row][right_column] == 255):
							patch_right = self.getImagePatch(self.right,row,right_column)
							patch_diff = (patch_left - patch_right)**2
							diff_value = np.floor(np.sqrt(np.sum(patch_diff)))
							if(diff_value < min_diff):
								min_diff = diff_value
								min_x = row
								min_y = right_column

					if(min_diff < 255):
						self.result[min_x][min_y] = 255
						self.matchedPoints.append([(row,column),(min_x,min_y),min_diff])
						print 'min_diff: ' + str(min_diff)
		return self.matchedPoints
  

	def setPointsOfInterest(self):
		if (self.left is None or self.right is None):
			print('Images not set')
			return

		self.borders_left = cv2.Canny(self.left,100,200)
		self.borders_right = cv2.Canny(self.right,100,200)


	def getPointsOfInterest(self):
		return [
			self.borders_left,
			self.borders_right
		]

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

class BorderStereoMatcher:
	def __init__(self):
		self.image1 = None
		self.image2 = None

	def set_images(self, image1, image2):
		self.image2 = image2
		self.image1 = image1

	def set_calibration_data(self, data):
		self.calibration_data = data

	def get_matching_points(self):
		border_image1 = self.__get_border_image(self.image1)
		border_image2 = self.__get_border_image(self.image2)

		border_image1_thresholded = self.__remove_points(border_image1)

		rectify_scale = 0  # 0=full crop, 1=no crop
		R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(self.calibration_data["cameraMatrix1"], self.calibration_data["distCoeffs1"],
														  self.calibration_data["cameraMatrix2"], self.calibration_data["distCoeffs2"], (1280, 720),
														  self.calibration_data["R"], self.calibration_data["T"], alpha=rectify_scale)

		points = np.array(cv2.findNonZero(border_image1_thresholded), dtype=np.float32)

		lines1 = cv2.computeCorrespondEpilines(points, 1, self.calibration_data['F'])
		lines1 = lines1.reshape(-1, 3)

		left_points, right_points, lines_right = self.__match_points(points, lines1, cv2.cvtColor(self.image1, cv2.COLOR_BGR2GRAY), cv2.cvtColor(self.image2, cv2.COLOR_BGR2GRAY), border_image2)

		# right_img_lines, left_img_lines = drawlines(border_image2, border_image1_thresholded, lines_right, right_points, left_points)

		points4D = cv2.triangulatePoints(P1, P2, left_points, right_points)
		final_points = []
		for index in range(0, right_points.shape[0] - 1):
			final_points.append(jderobot.RGBPoint(float(points4D[0][index] / points4D[3][index]), float(points4D[1][index] / points4D[3][index]), float(points4D[2][index] / points4D[3][index])))

		print(final_points)

		# Save the calibration matrix in a yaml file.
		if not os.path.exists('bin/Points/'):
			os.makedirs('bin/Points/')
		with open('bin/Points/points.yml', 'w') as outfile:
			yaml.dump(
				{'points': final_points}, outfile,
				default_flow_style=False)

	def __get_border_image(self, image):
		return cv2.Canny(image,100,200)

	def showTwoImages(self, image1, image2):
		result = np.concatenate((image1, image2), 1)
		cv2.namedWindow('result',cv2.WINDOW_NORMAL)
		cv2.resizeWindow('result',1300,600)
		cv2.imshow('result',result)
		cv2.waitKey(0)

	def __remove_points(self, image, patch_size = 40):
		height, width = image.shape
		result = np.zeros((height, width), np.uint8)
		for row in range(10 + patch_size,height - (10 + patch_size)):
			for column in range(10 + patch_size,width - (10 + patch_size)):
				if image[row][column] == 255:
					result[row][column] = 255
					image[row-patch_size:row+patch_size,column-patch_size:column+patch_size] = 0

		return result

	def __match_points(self, points, lines, image1, image2, image2_borders):
		height, width = image2.shape
		points_left = None
		points_right = None
		lines_right = None
		for line, point in zip(lines, points):
			left_patch = self.__get_image_patch(image1, point[0][1], point[0][0], 10)
			best_mean_square_error = 100000
			best_point = None
			for column in range(20, width - 20):
				row = int((-(column * line[0]) - line[2]) / line[1])
				if image2_borders[row][column] == 255:
					right_patch = self.__get_image_patch(image2, row, column, 10)
					if right_patch.shape == (20,20):
						mean_square_error = (np.square(right_patch - left_patch)).mean(axis=None)
						if mean_square_error < 80 and mean_square_error < best_mean_square_error:
							best_mean_square_error = mean_square_error
							best_point = np.array([[column, row]], dtype=np.float32)
			if best_point is not None:
				if points_left is None:
					points_left = np.array([point])
					points_right = np.array([best_point])
					lines_right = np.array([line])
				else:
					points_left = np.append(points_left, [point], axis=0)
					points_right = np.append(points_right, [best_point], axis=0)
					lines_right = np.append(lines_right, [line], axis=0)


		return points_left, points_right, lines_right

	def __get_image_patch(self,image,position_x,position_y,size = 3):
		return image[position_x-size:position_x+size,position_y-size:position_y+size]