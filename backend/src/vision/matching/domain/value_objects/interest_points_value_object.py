import cv2
import numpy as np


class InterestPointsValueObject:
    def __init__(self, image, sampling=None):
        self.image = self.__calculate_interest_points_image(image, sampling)
        self.interest_points = self.__calculate_interest_points_from_image()
        self.interest_points_row_index = None

    def get_interest_points_image(self):
        return self.image

    def get_interest_points(self):
        return self.interest_points

    def get_interest_points_row_index(self):
        if self.interest_points_row_index is None:
            self.__calculate_interest_points_by_row()

        return self.interest_points_row_index

    def get_interest_points_in_line(self, line):
        if self.interest_points_row_index is None:
            self.__calculate_interest_points_by_row()

        return self.__interest_points_in_line(line)

    def __calculate_interest_points_image(self, image, sampling):
        border_image = cv2.Canny(image, 100, 200)

        if sampling is not None:
            border_image = self.__remove_points(border_image, sampling)

        return border_image

    @staticmethod
    def __remove_points(image, patch_size=40):
        interest_points = np.array(cv2.findNonZero(image), dtype=np.float32)
        height, width = image.shape
        result = np.zeros((height, width), np.uint8)
        for point in interest_points:
            point_x = int(point[0][0])
            point_y = int(point[0][1])
            if image[point_y][point_x] == 255:
                top_border = (point_y - patch_size) if (point_y - patch_size) >= 0 else 0
                bottom_border = point_y + patch_size
                left_border = point_x - patch_size if point_x - patch_size >= 0 else 0
                right_border = point_x + patch_size
                image[top_border:bottom_border, left_border:right_border] = 0
                result[point_y][point_x] = 255

        return result

    def __calculate_interest_points_from_image(self):
        return np.array(cv2.findNonZero(self.image), dtype=np.float32)

    def __calculate_interest_points_by_row(self):
        non_zero_pixels_by_row = self.image.sum(axis=1) / 255
        non_zero_pixels_index = np.cumsum(non_zero_pixels_by_row)
        self.interest_points_row_index = non_zero_pixels_index

    def __interest_points_in_line(self, line):
        limits = [
            int((-(0 * line[0]) - line[2]) / line[1]),
            int((-(self.image.shape[1] * line[0]) - line[2]) / line[1])
        ]
        limits[1] = limits[1] if limits[1] < self.image.shape[0] - 1 else self.image.shape[0] - 1
        limits[0] = limits[0] if limits[0] < self.image.shape[0] - 1 else self.image.shape[0] - 1
        limits.sort()

        interest_points_in_range = self.interest_points[self.interest_points_row_index[limits[0] - 1]:self.interest_points_row_index[limits[1]]]

        line_function = np.array([
            [-line[0] / line[1]],
            [-1]
        ])

        new_array = np.dot(interest_points_in_range, line_function) - (line[2] / line[1])
        return new_array.astype(int), interest_points_in_range
