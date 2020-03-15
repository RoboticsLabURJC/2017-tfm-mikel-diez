import numpy as np
import cv2


class GetImageKeyPoints:
    def __init__(self):
        self.orb_detector = cv2.ORB_create()

    def execute(self, image, image_points):
        non_zero_pixels = np.array(cv2.findNonZero(image_points), dtype=np.float32)
        non_zero_pixels_by_row = image_points.sum(axis=1) / 255

        key_points = [cv2.KeyPoint(x[0][0], x[0][1], 1) for x in non_zero_pixels]

        key_points, descriptors = self.orb_detector.compute(image, key_points)

        return key_points, descriptors, non_zero_pixels, non_zero_pixels_by_row

