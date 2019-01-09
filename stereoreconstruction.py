# Here goes the imports
import numpy as np
import cv2
import yaml
import os

from Matching.imagematcher import ClassicMatcher

def imShowTwoImages(image1,image2):
    image = np.concatenate((image1, image2), axis=1)
    color = 0
    for index,line in enumerate(range(image1.shape[0]/10)):
        
        if(color > 255):
            color = 0
        cv2.line(image,(0,line*10),(1279,line*10),(color),1)
        color += 50
    cv2.imshow("rectified images", image)


# Here goes the script
if __name__ == '__main__':
	# Take the images from folder/camera and rectify
	with open("calibrated_camera.yml", 'r') as stream:
		try:
			data = yaml.load(stream)

			print data['F']
			print data['T']
			print data['F'] * data['T']

			rectify_scale = 0 # 0=full crop, 1=no crop
			R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(data["cameraMatrix1"], data["distCoeffs1"], data["cameraMatrix2"], data["distCoeffs2"], (640, 480), data["R"], data["T"], alpha = rectify_scale)

			left_maps = cv2.initUndistortRectifyMap(data["cameraMatrix1"], data["distCoeffs1"], R1, P1, (640, 480), cv2.CV_16SC2)
			right_maps = cv2.initUndistortRectifyMap(data["cameraMatrix2"], data["distCoeffs2"], R2, P2, (640, 480), cv2.CV_16SC2)

			img_left = cv2.imread('Images/left_image_2.png')
			img_right = cv2.imread('Images/right_image_2.png')

			gray_left = cv2.cvtColor(img_left,cv2.COLOR_BGR2GRAY)
			gray_right = cv2.cvtColor(img_right,cv2.COLOR_BGR2GRAY)

			left_img_remap = cv2.remap(gray_left, left_maps[0], left_maps[1], cv2.INTER_LANCZOS4)
			right_img_remap = cv2.remap(gray_right, right_maps[0], right_maps[1], cv2.INTER_LANCZOS4)

			imShowTwoImages(left_img_remap,right_img_remap)
			cv2.waitKey(0)

		except yaml.YAMLError as exc:
			print(exc)

	# Find matching points in both cameras
	matcher = ClassicMatcher()
	matcher.setImages(left_img_remap,right_img_remap)
	matcher.setPointsOfInterest()
	images = matcher.getPointsOfInterest()
	imShowTwoImages(images[0],images[1])
	cv2.waitKey(0)
	print matcher.matchPoints()
	matcher.showImages()
	# Get the 3d space points from 2d pixel pairs

	# Print the points in some kind of graphic interface
