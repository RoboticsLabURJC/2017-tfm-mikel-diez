import cv2
import numpy as np


class MatchInterestPointsByBruteForceInEpilineService:
    def __init__(self, height, width, interest_points_b, interest_points_b_index):
        self.matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        self.height = height
        self.width = width
        self.interest_points_b = interest_points_b
        self.interest_points_b_index = interest_points_b_index

    def execute(self, key_point_a, epiline):

        limits = [
            int((-(0 * epiline[0]) - epiline[2]) / epiline[1]),
            int((-(self.width * epiline[0]) - epiline[2]) / epiline[1])
        ]
        limits[1] = limits[1] if limits[1] < self.height - 1 else self.height - 1
        limits[0] = limits[0] if limits[0] < self.height - 1 else self.height - 1
        limits.sort()

        print(len(self.interest_points_b))

        interest_points_in_range = self.interest_points_b[self.interest_points_b_index[limits[0] - 1]:self.interest_points_b_index[limits[1]]]

        print(len(interest_points_in_range))

        line_function = np.array([
            [-epiline[0] / epiline[1]],
            [-1]
        ])

        new_array = np.dot(interest_points_in_range, line_function) - (epiline[2] / epiline[1])
        new_array = new_array.astype(int)

