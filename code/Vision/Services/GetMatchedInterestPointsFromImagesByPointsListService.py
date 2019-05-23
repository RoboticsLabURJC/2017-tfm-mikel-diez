import cv2
import numpy as np
import logging
import cProfile
from Vision.Components.GUI.Helpers import imShowTwoImages, drawlines
from datetime import datetime

class GetMatchedInterestPointsFromImagesService:
    def __init__(self, stereo_calibration, camera_a_calibration, camera_b_calibration):
        self.stereo_calibration = stereo_calibration
        self.camera_a_calibration = camera_a_calibration
        self.camera_b_calibration = camera_b_calibration

    def execute(self, image_a, image_b):
        image_a_borders = self.__get_border_image(image_a)
        image_b_borders = self.__get_border_image(image_b)

        image_a_borders_sampled = self.__remove_points(image_a_borders, 5)

        interest_points_a = np.array(cv2.findNonZero(image_a_borders_sampled), dtype=np.float32)
        interest_points_b, interest_points_b_by_row, interest_points_b_index = self.get_right_points_structure(image_b_borders)

        epilines_a = cv2.computeCorrespondEpilines(interest_points_a, 1, self.stereo_calibration['F'])
        epilines_a = epilines_a.reshape(-1, 3)

        logging.info('[{}] Start Match Points With Template'.format(datetime.now().time()))
        pr = cProfile.Profile()
        pr.enable()
        left_points, right_points = self.__get_matched_points_with_image_b_map(
            interest_points_a,
            interest_points_b,
            interest_points_b_index,
            epilines_a,
            image_a,
            image_b
        )

        pr.disable()
        pr.print_stats()

        logging.info('[{}] End Match Points With Template'.format(datetime.now().time()))
        logging.info('[{}] Points to be Matched'.format(interest_points_a.shape[0]))
        logging.info('[{}] Points Matched'.format(left_points.shape[0]))

        return left_points, right_points

    @staticmethod
    def __get_border_image(image):
        return cv2.Canny(image,100,200)

    @staticmethod
    def __remove_points(image, patch_size = 40):
        height, width = image.shape
        result = np.zeros((height, width), np.uint8)
        for row in range(10 + patch_size,height - (10 + patch_size)):
            for column in range(10 + patch_size,width - (10 + patch_size)):
                if image[row][column] == 255:
                    result[row][column] = 255
                    image[row-patch_size:row+patch_size,column-patch_size:column+patch_size] = 0

        return result

    @staticmethod
    def get_right_points_structure(border_image):
        non_zero_pixels = np.array(cv2.findNonZero(border_image), dtype=np.float32)
        non_zero_pixels_by_row = border_image.sum(axis=1) / 255
        non_zero_pixels_index = np.cumsum(non_zero_pixels_by_row)
        return non_zero_pixels, non_zero_pixels_by_row, non_zero_pixels_index

    def __get_matched_points_with_image_b_map(self, points_a, points_b, points_b_index, lines, image_a, image_b):
        height, width, depth = image_a.shape
        result_points_a = []
        result_points_b = []
        patch_size = 20

        for line, point in zip(lines, points_a):
            left_patch = self.__get_image_patch(
                image_a,
                point[0][1],
                point[0][0],
                int(patch_size / 2),
                int(patch_size / 2)
            )

            limits = [
                int((-(0 * line[0]) - line[2]) / line[1]),
                int((-(width * line[0]) - line[2]) / line[1])
            ]
            limits[1] = limits[1] if limits[1] < image_a.shape[0] - 1 else image_a.shape[0] - 1
            limits[0] = limits[0] if limits[0] < image_a.shape[0] - 1 else image_a.shape[0] - 1
            limits.sort()

            interest_points_in_range = points_b[points_b_index[limits[0] - 1]:points_b_index[limits[1]]]

            line_function = np.array([
                [-line[0] / line[1]],
                [-1]
            ])

            new_array = np.dot(interest_points_in_range, line_function) - (line[2] / line[1])
            new_array = new_array.astype(int)
            if np.where(new_array == 0)[0].size is not 0:
                # print(interest_points_in_range[np.where(new_array == 0)[0]])
                interest_points_in_line = np.unique(interest_points_in_range[np.where(new_array == 0)[0]], axis=0)
                interest_patch_array = np.zeros((20 * interest_points_in_line.shape[0], 20, 3))
                for index, interest_point in enumerate(interest_points_in_line):
                    right_patch = self.__get_image_patch(
                        image_b,
                        interest_point[0][1],
                        interest_point[0][0],
                        int(patch_size / 2),
                        int(patch_size / 2)
                    )
                    if right_patch.shape == (patch_size, patch_size, 3):
                        interest_patch_array[20 * index:20 * (index + 1), 0:20, :] = right_patch

                line_match = cv2.matchTemplate(interest_patch_array.astype('uint8'), left_patch, cv2.TM_CCORR_NORMED)
                interest_values = np.arange(0, interest_points_in_line.shape[0]) * 20

                minVal, maxVal, minPos, maxPos = cv2.minMaxLoc(line_match[interest_values])

                if maxVal > 0.99:
                    result_points_a.append(point)
                    result_points_b.append(interest_points_in_line[interest_values[maxPos[1]] / 20])

        return np.array(result_points_a), np.array(result_points_b)

    @staticmethod
    def __match_column_patch(needle, haystack):
        similarities = cv2.matchTemplate(haystack, needle, cv2.TM_CCORR_NORMED)
        __, maxVal, __, maxLoc = cv2.minMaxLoc(similarities)
        return maxVal, maxLoc

    @staticmethod
    def __get_image_patch(image, position_x, position_y, height, width, depth = 1):
        return image[int(position_x-width):int(position_x+width), int(position_y-height):int(position_y+height), :]
