import numpy as np
import cv2
import jderobot
import os
import yaml
from Vision.Components.GUI.Helpers import imShowTwoImages, drawlines
import logging
from datetime import datetime
import math


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

		border_image1_thresholded = self.__remove_points(border_image1, 5)

		origen = np.array([np.array([1]), np.array([0]), np.array([0])])

		# This should go in the calibration procedure or at least it shouldn't be done several times
		rectify_scale = 0  # 0=full crop, 1=no crop
		r1, r2, p1, p2, q, roi1, roi2 = cv2.stereoRectify(
			self.calibration_data["cameraMatrix1"],
			self.calibration_data["distCoeffs1"],
			self.calibration_data["cameraMatrix2"],
			self.calibration_data["distCoeffs2"],
			border_image1.shape[::-1],
			self.calibration_data["R"],
			self.calibration_data["T"],
			alpha=rectify_scale
		)
		#
		# cameraMatrix, rotMatrix, transVect, rotMatrixX, rotMatrixY, rotMatrixZ, eulerAngles = cv2.decomposeProjectionMatrix(p1)
		# cameraMatrix2, rotMatrix2, transVect2, rotMatrixX2, rotMatrixY2, rotMatrixZ2, eulerAngles2 = cv2.decomposeProjectionMatrix(p2)
		#
		# print(cameraMatrix)
		# print(rotMatrix)
		# print(transVect)
		#
		# print(cameraMatrix2)
		# print(rotMatrix2)
		# print(transVect2)

		# second_camera = transVect[0:3, :] / transVect[3, :]

		points = np.array(cv2.findNonZero(border_image1_thresholded), dtype=np.float32)

		lines1 = cv2.computeCorrespondEpilines(points, 1, self.calibration_data['F'])
		lines1 = lines1.reshape(-1, 3)

		logging.info('[{}] Start Match Points With Template'.format(datetime.now().time()))
		left_points, right_points, lines_right = self.__match_points_hsv_template(points, lines1, self.image1, self.image2, border_image2)
		logging.info('[{}] End Match Points With Template'.format(datetime.now().time()))

		# self.__show_matching_points_with_lines(self.image1, self.image2, left_points, right_points)

		logging.info('[{}] Start Undistort Points'.format(datetime.now().time()))
		undistorted_left_points = cv2.undistortPoints(
			left_points,
			self.calibration_data["cameraMatrix1"],
			self.calibration_data["distCoeffs1"],
			R=r1,
			P=p1
		)
		undistorted_right_points = cv2.undistortPoints(
			right_points,
			self.calibration_data["cameraMatrix2"],
			self.calibration_data["distCoeffs2"],
			R=r2,
			P=p2
		)

		logging.info('[{}] End Undistort Points'.format(datetime.now().time()))

		logging.info('[{}] Start Triangulate Points'.format(datetime.now().time()))
		points4d = cv2.triangulatePoints(p2, p1, undistorted_left_points, undistorted_right_points)
		logging.info('[{}] End Triangulate Points'.format(datetime.now().time()))
		final_points = []
		logging.info('[{}] Convert Poinst from homogeneus coordiantes to cartesian and JdeRobot points'.format(datetime.now().time()))
		ourworldtransformation = np.array([
			np.array([1., .0, .0, .0]),
			np.array([.0, .0, 1., .0]),
			np.array([.0, -1., .0, .0]),
			np.array([.0, .0, .0, .1])
		])

		points4d = points4d.T.dot(ourworldtransformation).T

		for index in range(0, right_points.shape[0] - 0):
			red = float(self.image2[int(left_points[index][0][1])][int(left_points[index][0][0])][2]/255.0)
			green = float(self.image2[int(left_points[index][0][1])][int(left_points[index][0][0])][1]/255.0)
			blue = float(self.image2[int(left_points[index][0][1])][int(left_points[index][0][0])][0]/255.0)
			final_points.append(jderobot.RGBPoint(float(points4d[0][index] / points4d[3][index]), float(points4d[1][index] / points4d[3][index]), float(points4d[2][index] / points4d[3][index]), red, green, blue))
		logging.info('[{}] End Convert Poinst from homogeneus coordiantes to cartesian'.format(datetime.now().time()))
		# self.persistPoints(final_points)


		logging.info('[{}] Return cartesian reconstructed points'.format(datetime.now().time()))
		return final_points

	def persistPoints(self, final_points):
		logging.info('[{}] Persist points'.format(datetime.now().time()))
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

	def __match_points_gray(self, points, lines, image1, image2, image2_borders):
		height, width = image2.shape
		points_left = None
		points_right = None
		lines_right = None
		for line, point in zip(lines, points):
			left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
			best_mean_square_error = 100000
			best_point = None
			for column in range(20, width - 20):
				row = int((-(column * line[0]) - line[2]) / line[1])
				if image2_borders[row][column] == 255:
					right_patch = self.__get_image_patch_gray(image2, row, column, 10)
					if right_patch.shape == (20,20):
						mean_square_error = (np.square(right_patch - left_patch)).mean(axis=None)
						if mean_square_error < 70 and mean_square_error < best_mean_square_error:
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

	def __match_points_bgr(self, points, lines, image1, image2, image2_borders):
		height, width, depth = image2.shape
		points_left = None
		points_right = None
		lines_right = None
		for line, point in zip(lines, points):
			left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
			best_mean_square_error = 100000
			best_point = None
			for column in range(20, width - 20):
				row = int((-(column * line[0]) - line[2]) / line[1])
				for epiline_offset in range(-4, 4):
					if image2_borders[row][column + epiline_offset] == 255:
						right_patch = self.__get_image_patch_gray(image2, row, column + epiline_offset, 10)
						other_image = cv2.matchTemplate(right_patch, left_patch, cv2.TM_CCOEFF)
						print(other_image[0][0])
						cv2.namedWindow('result', cv2.WINDOW_NORMAL)
						cv2.resizeWindow('result', 1300, 600)
						cv2.imshow('result', other_image)
						cv2.waitKey(0)
						if right_patch.shape == (20, 20, 3):
							mean_square_error = (np.square(right_patch - left_patch)).mean(axis=None)
							if mean_square_error < 80 and mean_square_error < best_mean_square_error:
								best_mean_square_error = mean_square_error
								best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
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

	def __match_points_bgr_template(self, points, lines, image1, image2, image2_borders):
		height, width, depth = image2.shape
		points_left = None
		points_right = None
		lines_right = None
		for line, point in zip(lines, points):
			left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
			best_mean_square_error = 0.9
			best_point = None
			for column in range(20, width - 20):
				row = int((-(column * line[0]) - line[2]) / line[1])
				for epiline_offset in range(-4, 4):
					if image2_borders[row][column + epiline_offset] == 255:
						right_patch = self.__get_image_patch_gray(image2, row, column + epiline_offset, 10)
						if right_patch.shape == (20, 20, 3):
							similarity = cv2.matchTemplate(right_patch, left_patch, cv2.TM_SQDIFF_NORMED)
							similarity = similarity[0][0]
							if similarity < 0.1 and similarity < best_mean_square_error:
								best_mean_square_error = similarity
								best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
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

	def __match_points_hsv(self, points, lines, image1, image2, image2_borders):
		height, width, depth = image2.shape
		points_left = None
		points_right = None
		lines_right = None
		image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
		image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
		for line, point in zip(lines, points):
			left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
			best_mean_square_error = 100000
			best_point = None
			for column in range(20, width - 20):
				row = int((-(column * line[0]) - line[2]) / line[1])
				if image2_borders[row][column] == 255:
					right_patch = self.__get_image_patch_gray(image2, row, column, 10)
					if right_patch.shape == (20, 20, 3):
						error = self.__calculate_mean_square_error_hsv(left_patch, right_patch)
						if error < 25 and error < best_mean_square_error:
							best_mean_square_error = error
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

	def __match_points_hsv_template(self, points, lines, image1, image2, image2_borders):
		height, width, depth = image2.shape
		points_left = None
		points_right = None
		lines_right = None
		image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
		image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
		for line, point in zip(lines, points):
			left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
			best_mean_square_error = 0.9
			best_point = None
			for column in range(20, width - 20):
				row = int((-(column * line[0]) - line[2]) / line[1])
				for epiline_offset in range(-1, 1):
					if (row) < image2_borders.shape[1] and (row) > 0:
						if image2_borders[row][column + epiline_offset] == 255:
							right_patch = self.__get_image_patch_gray(image2, row, column, 10)
							if right_patch.shape == (20, 20, 3):
								similarity = cv2.matchTemplate(right_patch, left_patch, cv2.TM_CCORR_NORMED)
								similarity = similarity[0][0]
								if similarity > 0.9 and similarity > best_mean_square_error:
									best_mean_square_error = similarity
									best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
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

	def __get_image_patch_gray(self, image, position_x, position_y, size = 3):
		return image[int(position_x)-size:int(position_x)+size, int(position_y)-size:int(position_y)+size]

	def __get_image_patch_rgb(self, image, position_x, position_y, size = 3):
		return image[position_x-size:position_x+size, position_y-size:position_y+size, :]

	def __show_matching_points_with_lines(self, image1, image2, points1, points2):
		result = np.concatenate((image1, image2), 1)
		for pt1, pt2 in zip(points1, points2):
			color = tuple(np.random.randint(0, 255, 3).tolist())
			result = cv2.circle(result, tuple(pt1[0]), 10, color, 3)
			result = cv2.circle(result, (int(pt2[0][0] + 1280.), int(pt2[0][1])), 10, color, 3)
			result = cv2.line(result, tuple(pt1[0]), (int(pt2[0][0] + 1280.), int(pt2[0][1])), color, 2)

		cv2.namedWindow('Match Points', cv2.WINDOW_NORMAL)
		cv2.resizeWindow('Match Points', 1300, 600)
		cv2.imshow('Match Points', result)
		cv2.waitKey(0)

	def __calculate_mean_square_error_hsv(self, left_patch, right_patch):
		height, width, depth = left_patch.shape
		accumulated_error = 0
		for row in range(0, height -1):
			for column in range(0, width - 1):
				accumulated_error += abs(self.round_difference(left_patch[row][column][0], right_patch[row][column][0]))
				accumulated_error += abs(left_patch[row][column][1] - right_patch[row][column][1])
		return accumulated_error / (height * width * 2)

	def round_difference(self, angle1, angle2):
		return 180 - abs(abs(angle1 - angle2) - 180)