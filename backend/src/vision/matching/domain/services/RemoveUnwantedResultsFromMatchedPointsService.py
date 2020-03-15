import math
import cv2
import numpy as np


class RemoveUnwantedResultsFromMatchedPointsService:
    def __init__(self, calibration_data):
        self.calibration_data = calibration_data

    def execute(self, points_a, points_b, image_a, image_b):
        points_a_filtered = []
        points_b_filtered = []

        r, c, d = image_a.shape

        epipolar_lines_b = cv2.computeCorrespondEpilines(points_b, 2, self.calibration_data['F'])
        epipolar_lines_b = epipolar_lines_b.reshape(-1, 3)

        epipolar_lines_a = cv2.computeCorrespondEpilines(points_a, 1, self.calibration_data['F'])
        epipolar_lines_a = epipolar_lines_a.reshape(-1, 3)

        for point_a, point_b, line_b, line_a in zip(points_a, points_b, epipolar_lines_b, epipolar_lines_a):
            color_a = tuple(np.random.randint(0, 255, 3).tolist())
            color_b = tuple(np.random.randint(0, 255, 3).tolist())
            x0, y0 = map(int, [0, -line_b[2] / line_b[1]])
            x1, y1 = map(int, [c, -(line_b[2] + line_b[0] * c) / line_b[1]])
            image_a_epiline = image_a.copy()
            image_b_epiline = image_b.copy()
            cv2.line(image_a_epiline, (x0, y0), (x1, y1), color_b, 3)
            x0, y0 = map(int, [0, -line_a[2] / line_a[1]])
            x1, y1 = map(int, [c, -(line_a[2] + line_a[0] * c) / line_a[1]])
            cv2.line(image_b_epiline, (x0, y0), (x1, y1), color_a, 3)
            cv2.circle(image_a_epiline, (int(point_a[0][0]), int(point_a[0][1])), 8, color_a, -1)
            cv2.circle(image_b_epiline, (int(point_b[0][0]), int(point_b[0][1])), 8, color_b, -1)
            self.showTwoImages(image_a_epiline, image_b_epiline)
            if self.get_shortest_distance_line_to_point(point_a[0][0], point_a[0][1], line_b[0], line_b[1], line_b[2]) < 0.1:
                points_a_filtered.append(point_a)
                points_b_filtered.append(point_b)

        return np.array(points_a_filtered), np.array(points_b_filtered)

    def get_shortest_distance_line_to_point(self, x, y, a, b, c):
        return abs((a * x + b * y + c)) / (math.sqrt(a * a + b * b))

    def showTwoImages(self, image1, image2):
        result = np.concatenate((image1, image2), 1)
        cv2.namedWindow('result',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('result',1300,600)
        cv2.imshow('result',result)
        cv2.waitKey(0)
