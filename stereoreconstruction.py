# Here goes the imports
import numpy as np
import cv2

from Matching.imagematcher import ClassicMatcher

# Here goes the script
if __name__ == '__main__':
	# Take the images from folder/camera

	# Find matching points in both cameras
	matcher = ClassicMatcher()
	matcher.setImages(cv2.imread('./test/images/left.png'),cv2.imread('./test/images/right.png'))
	matcher.matchPoints()
	matcher.showImages()
	# Get the 3d space points from 2d pixel pairs

	# Print the points in some kind of graphic interface
