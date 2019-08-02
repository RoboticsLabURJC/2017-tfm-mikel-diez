import cv2
import yaml
import sys
import numpy as np

from src.vision.presentation.services.Helpers import imShowTwoImages, drawlines


if __name__ == '__main__':
    image_a = cv2.imread('bin/sets/set_10y_center/images/left_image_1.png')
    image_b = cv2.imread('bin/sets/set_10y_center/images/right_image_1.png')

    point_a = np.array([[[1178, 338]]], dtype=np.float32)
    point_b = np.array([[[705, 437]]], dtype=np.float32)

    with open("bin/sets/set_10y_center/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream, Loader=yaml.UnsafeLoader)

            gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
            gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)

            epilines = cv2.computeCorrespondEpilines(point_a, 1, data['F'])
            epilines = epilines.reshape(-1, 3)

            left_img_lines, right_img_lines = drawlines(gray_a, gray_b, epilines, point_a, point_b)

            imShowTwoImages(left_img_lines, right_img_lines, 'wiiii')
            cv2.waitKey(0)

        except yaml.YAMLError as exc:
            print(exc)





