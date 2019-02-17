# Here goes the imports
import numpy as np
import cv2
import yaml
import os

from Modules.Matching.imagematcher import ClassicMatcher
from Modules.GUI.Helpers import imShowTwoImages, drawlines

if __name__ == '__main__':
	# Take the images from folder/camera and rectify
	with open("bin/CalibrationMatrix/set11/calibrated_camera.yml", 'r') as stream:
		try:
			data = yaml.load(stream)

			print(data.keys())

			print('R', data['R'])
			print('T', data['T'])
			print('F', data['F'])
			print('cameraMatrix1', data['cameraMatrix1'])
			print('cameraMatrix2', data['cameraMatrix2'])

			rectify_scale = 0 # 0=full crop, 1=no crop
			R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(data["cameraMatrix1"], data["distCoeffs1"], data["cameraMatrix2"], data["distCoeffs2"], (640, 480), data["R"], data["T"], alpha = rectify_scale)

			left_maps = cv2.initUndistortRectifyMap(data["cameraMatrix1"], data["distCoeffs1"], R1, P1, (1920, 1080), cv2.CV_16SC2)
			right_maps = cv2.initUndistortRectifyMap(data["cameraMatrix2"], data["distCoeffs2"], R2, P2, (1920, 1080), cv2.CV_16SC2)

			img_left = cv2.imread('bin/CalibrationImages/set11_objectReconstruction/left_image_3.png')
			img_right = cv2.imread('bin/CalibrationImages/set11_objectReconstruction/right_image_3.png')

			imShowTwoImages(img_left, img_right, 'original imgs')
			cv2.waitKey(0)

			gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
			gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

			left_img_remap = cv2.remap(gray_left, left_maps[0], left_maps[1], cv2.INTER_LANCZOS4)
			right_img_remap = cv2.remap(gray_right, right_maps[0], right_maps[1], cv2.INTER_LANCZOS4)

			imShowTwoImages(gray_left, gray_right, 'original grey')
			cv2.waitKey(0)

			imShowTwoImages(left_img_remap,right_img_remap, 'remapped images')
			cv2.waitKey(0)

			lines1 = cv2.computeCorrespondEpilines((0, 0, 0), 1, data['F'])
			lines1 = lines1.reshape(-1, 3)
			left_img_lines, right_img_lines = drawlines(left_img_remap, right_img_remap, lines1, pts1, pts2)

		except yaml.YAMLError as exc:
			print(exc)