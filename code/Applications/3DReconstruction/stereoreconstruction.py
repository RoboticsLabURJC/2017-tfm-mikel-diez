# Here goes the imports
import numpy as np
import cv2
import yaml

from Modules.GUI.Helpers import imShowTwoImages, drawlines

if __name__ == '__main__':
	# Take the images from folder/camera and rectify
	with open("bin/CalibrationMatrix/set12/calibrated_camera.yml", 'r') as stream:
		try:
			data = yaml.load(stream)

			print(data.keys())

			print('R', data['R'])
			print('T', data['T'])
			print('F', data['F'])
			print('cameraMatrix1', data['cameraMatrix1'])
			print('cameraMatrix2', data['cameraMatrix2'])

			rectify_scale = 0 # 0=full crop, 1=no crop
			R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(data["cameraMatrix1"], data["distCoeffs1"], data["cameraMatrix2"], data["distCoeffs2"], (1280, 720), data["R"], data["T"], alpha = rectify_scale)

			left_maps = cv2.initUndistortRectifyMap(data["cameraMatrix1"], data["distCoeffs1"], R1, P1, (1280, 720), cv2.CV_16SC2)
			right_maps = cv2.initUndistortRectifyMap(data["cameraMatrix2"], data["distCoeffs2"], R2, P2, (1280, 720), cv2.CV_16SC2)

			img_left = cv2.imread('bin/CalibrationImages/set12_objectReconstruction/left_image_16.png')
			img_right = cv2.imread('bin/CalibrationImages/set12_objectReconstruction/right_image_16.png')

			imShowTwoImages(img_left, img_right, 'original imgs')
			cv2.waitKey(0)

			gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
			gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

			left_img_remap = cv2.remap(gray_left, left_maps[0], left_maps[1], cv2.INTER_LANCZOS4)
			right_img_remap = cv2.remap(gray_right, right_maps[0], right_maps[1], cv2.INTER_LANCZOS4)

			# imShowTwoImages(gray_left, gray_right, 'original grey')
			# cv2.waitKey(0)
			#
			# imShowTwoImages(left_img_remap,right_img_remap, 'remapped images')
			# cv2.waitKey(0)

			points = np.array([[[858, 271]], [[897, 453]], [[1090, 276]], [[1123, 444]]], dtype=np.float32)
			points2 = np.array([[[709, 255]], [[733, 432]], [[949, 265]], [[969, 430]]], dtype=np.float32)

			lines1 = cv2.computeCorrespondEpilines(points, 1, data['F'])
			lines1 = lines1.reshape(-1, 3)
			print(lines1)
			# right_img_lines, left_img_lines = drawlines(gray_right, gray_left, lines1, points, points)

			# imShowTwoImages(left_img_lines, right_img_lines, 'wiiii')
			# cv2.waitKey(0)

			points4D = cv2.triangulatePoints(P1, P2, points, points2)
			print(points4D)
			print(points)
			newArray = [np.array([-0.12184567, -0.14085074, -0.23511265]) / -0.24977995, np.array([ 0.00702684, -0.08393233,  0.00313828]) / -0.07938664, np.array([-0.99220562, -0.98608309, -0.97168368]) / -0.96471202, np.array([-0.02514401, -0.02750583, -0.0233017]) / -0.02526825]
			print(newArray)

		except yaml.YAMLError as exc:
			print(exc)