import numpy as np
import cv2
import os
import yaml
from Vision.Components.GUI.Helpers import imShowTwoImages, drawlines
import logging
from datetime import datetime

import cProfile

class BorderStereoMatcher:
    def __init__(self):
        self.image1 = None
        self.image2 = None

    def set_images(self, image1, image2):
        self.image2 = image2
        self.image1 = image1

    def set_calibration_data(self, stereoCalibration, cameraACalibration, cameraBCalibration):
        self.calibration_data = stereoCalibration
        self.camera_a_calibration = cameraACalibration
        self.camera_b_calibration = cameraBCalibration

    def get_matching_points(self, gui):
        border_image1 = self.__get_border_image(self.image1)
        border_image2 = self.__get_border_image(self.image2)

        border_image1_thresholded = self.__remove_points(border_image1, 5)

        points = np.array(cv2.findNonZero(border_image1_thresholded), dtype=np.float32)
        points_right = self.getRightPointsStructure(border_image2)

        lines1 = cv2.computeCorrespondEpilines(points, 1, self.calibration_data['F'])
        lines1 = lines1.reshape(-1, 3)

        logging.info('[{}] Start Match Points With Template'.format(datetime.now().time()))
        init_matching_time = datetime.now()
        pr = cProfile.Profile()
        pr.enable()
        left_points, right_points, lines_right = self.__match_points_with_epilines(points, lines1, self.image1, self.image2, border_image2)
        pr.disable()
        pr.print_stats()

        end_matching_time = datetime.now()
        logging.info('[{}] End Match Points With Template'.format(datetime.now().time()))
        logging.info('[{}] Points to be Matched'.format(points.shape[0]))
        logging.info('[{}] Points Matched'.format(left_points.shape[0]))
        gui.matching_information_points_to_match_label.setText('Points to match: %s' % points.shape[0])
        gui.matching_information_points_matched_label.setText('Points matched: %s' % left_points.shape[0])
        gui.matching_information_seconds_per_point_label.setText('Seconds per Point: %s' % ((end_matching_time - init_matching_time).total_seconds() / points.shape[0]))
        gui.matching_information_total_matching_seconds_label.setText('Total time (s): %s' % (end_matching_time - init_matching_time).total_seconds())
        # self.__show_matching_points_with_lines(self.image1, self.image2, left_points, right_points)

        return left_points, right_points

    def getRightPointsStructure(self, border_image):
        non_zero_pixels_structure = np.empty((border_image.shape[0],), dtype=object)
        non_zero_pixels_structure[...] = [[] for _ in range(border_image.shape[0])]
        non_zero_pixels = np.array(cv2.findNonZero(border_image), dtype=np.float32)
        for non_zero_pixel in non_zero_pixels:
            non_zero_pixels_structure[non_zero_pixel[0][1]].append(non_zero_pixel[0][0])
        return non_zero_pixels_structure

    def persistPoints(self, final_points):
        logging.info('[{}] Persist points'.format(datetime.now().time()))
        if not os.path.exists('bin/Points/'):
            os.makedirs('bin/Points/')
        with open('bin/Points/points.yml', 'w') as outfile:
            yaml.dump(
                {'points': final_points}, outfile,
                default_flow_style=False)

    def __get_border_image(self, image):
        return cv2.Canny(image,100,200)

    def showTwoImages(self, image1, image2):
        result = np.concatenate((image1, image2), 1)
        cv2.namedWindow('result',cv2.WINDOW_NORMAL)
        cv2.resizeWindow('result',1300,600)
        cv2.imshow('result',result)
        cv2.waitKey(0)

    def __remove_points(self, image, patch_size = 40):
        height, width = image.shape
        result = np.zeros((height, width), np.uint8)
        for row in range(10 + patch_size,height - (10 + patch_size)):
            for column in range(10 + patch_size,width - (10 + patch_size)):
                if image[row][column] == 255:
                    result[row][column] = 255
                    image[row-patch_size:row+patch_size,column-patch_size:column+patch_size] = 0

        return result

    def __match_points_gray(self, points, lines, image1, image2, image2_borders):
        height, width = image2.shape
        points_left = None
        points_right = None
        lines_right = None
        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
            best_mean_square_error = 100000
            best_point = None
            for column in range(20, width - 20):
                row = int((-(column * line[0]) - line[2]) / line[1])
                if image2_borders[row][column] == 255:
                    right_patch = self.__get_image_patch_gray(image2, row, column, 10)
                    if right_patch.shape == (20,20):
                        mean_square_error = (np.square(right_patch - left_patch)).mean(axis=None)
                        if mean_square_error < 70 and mean_square_error < best_mean_square_error:
                            best_mean_square_error = mean_square_error
                            best_point = np.array([[column, row]], dtype=np.float32)
            if best_point is not None:
                if points_left is None:
                    points_left = np.array([point])
                    points_right = np.array([best_point])
                    lines_right = np.array([line])
                else:
                    points_left = np.append(points_left, [point], axis=0)
                    points_right = np.append(points_right, [best_point], axis=0)
                    lines_right = np.append(lines_right, [line], axis=0)


        return points_left, points_right, lines_right

    def __match_points_bgr(self, points, lines, image1, image2, image2_borders):
        height, width, depth = image2.shape
        points_left = None
        points_right = None
        lines_right = None
        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
            best_mean_square_error = 100000
            best_point = None
            for column in range(20, width - 20):
                row = int((-(column * line[0]) - line[2]) / line[1])
                for epiline_offset in range(-4, 4):
                    if image2_borders[row][column + epiline_offset] == 255:
                        right_patch = self.__get_image_patch_gray(image2, row, column + epiline_offset, 10)
                        other_image = cv2.matchTemplate(right_patch, left_patch, cv2.TM_CCOEFF)
                        print(other_image[0][0])
                        cv2.namedWindow('result', cv2.WINDOW_NORMAL)
                        cv2.resizeWindow('result', 1300, 600)
                        cv2.imshow('result', other_image)
                        cv2.waitKey(0)
                        if right_patch.shape == (20, 20, 3):
                            mean_square_error = (np.square(right_patch - left_patch)).mean(axis=None)
                            if mean_square_error < 80 and mean_square_error < best_mean_square_error:
                                best_mean_square_error = mean_square_error
                                best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
            if best_point is not None:
                if points_left is None:
                    points_left = np.array([point])
                    points_right = np.array([best_point])
                    lines_right = np.array([line])
                else:
                    points_left = np.append(points_left, [point], axis=0)
                    points_right = np.append(points_right, [best_point], axis=0)
                    lines_right = np.append(lines_right, [line], axis=0)


        return points_left, points_right, lines_right

    def __match_points_bgr_template(self, points, lines, image1, image2, image2_borders):
        height, width, depth = image2.shape
        points_left = None
        points_right = None
        lines_right = None
        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
            best_mean_square_error = 0.9
            best_point = None
            for column in range(20, width - 20):
                row = int((-(column * line[0]) - line[2]) / line[1])
                for epiline_offset in range(-4, 4):
                    if image2_borders[row][column + epiline_offset] == 255:
                        right_patch = self.__get_image_patch_gray(image2, row, column + epiline_offset, 10)
                        if right_patch.shape == (20, 20, 3):
                            similarity = cv2.matchTemplate(right_patch, left_patch, cv2.TM_SQDIFF_NORMED)
                            similarity = similarity[0][0]
                            if similarity < 0.1 and similarity < best_mean_square_error:
                                best_mean_square_error = similarity
                                best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
            if best_point is not None:
                if points_left is None:
                    points_left = np.array([point])
                    points_right = np.array([best_point])
                    lines_right = np.array([line])
                else:
                    points_left = np.append(points_left, [point], axis=0)
                    points_right = np.append(points_right, [best_point], axis=0)
                    lines_right = np.append(lines_right, [line], axis=0)


        return points_left, points_right, lines_right

    def __match_points_hsv(self, points, lines, image1, image2, image2_borders):
        height, width, depth = image2.shape
        points_left = None
        points_right = None
        lines_right = None
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], 10)
            best_mean_square_error = 100000
            best_point = None
            for column in range(20, width - 20):
                row = int((-(column * line[0]) - line[2]) / line[1])
                if image2_borders[row][column] == 255:
                    right_patch = self.__get_image_patch_gray(image2, row, column, 10)
                    if right_patch.shape == (20, 20, 3):
                        error = self.__calculate_mean_square_error_hsv(left_patch, right_patch)
                        if error < 25 and error < best_mean_square_error:
                            best_mean_square_error = error
                            best_point = np.array([[column, row]], dtype=np.float32)
            if best_point is not None:
                if points_left is None:
                    points_left = np.array([point])
                    points_right = np.array([best_point])
                    lines_right = np.array([line])
                else:
                    points_left = np.append(points_left, [point], axis=0)
                    points_right = np.append(points_right, [best_point], axis=0)
                    lines_right = np.append(lines_right, [line], axis=0)


        return points_left, points_right, lines_right

    def __match_points_hsv_template(self, points, lines, image1, image2, image2_borders):
        height, width, depth = image2.shape
        points_left = None
        points_right = None
        lines_right = None
        patch_size = 20
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], int(patch_size / 2))
            best_mean_square_error = 0.9
            best_point = None
            for column in range(patch_size, width - patch_size):
                row = int((-(column * line[0]) - line[2]) / line[1])
                for epiline_offset in range(-1, 1):
                    if 0 < row < image2_borders.shape[1]:
                        if image2_borders[row][column + epiline_offset] == 255:
                            right_patch = self.__get_image_patch_gray(image2, row, column, int(patch_size / 2))
                            if right_patch.shape == (patch_size, patch_size, 3):
                                similarity = cv2.matchTemplate(right_patch, left_patch, cv2.TM_CCORR_NORMED)
                                similarity = similarity[0][0]
                                if similarity > 0.9 and similarity > best_mean_square_error:
                                    best_mean_square_error = similarity
                                    best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
            if best_point is not None:
                if points_left is None:
                    points_left = np.array([point])
                    points_right = np.array([best_point])
                    lines_right = np.array([line])
                else:
                    points_left = np.append(points_left, [point], axis=0)
                    points_right = np.append(points_right, [best_point], axis=0)
                    lines_right = np.append(lines_right, [line], axis=0)


        return points_left, points_right, lines_right

    def __get_image_patch_gray(self, image, position_x, position_y, size = 3):
        return image[int(position_x)-size:int(position_x)+size, int(position_y)-size:int(position_y)+size]

    def __get_image_patch_rgb(self, image, position_x, position_y, size = 3):
        return image[position_x-size:position_x+size, position_y-size:position_y+size, :]

    def __show_matching_points_with_lines(self, image1, image2, points1, points2):
        result = np.concatenate((image1, image2), 1)
        for pt1, pt2 in zip(points1, points2):
            color = tuple(np.random.randint(0, 255, 3).tolist())
            result = cv2.circle(result, tuple(pt1[0]), 10, color, 3)
            result = cv2.circle(result, (int(pt2[0][0] + 1280.), int(pt2[0][1])), 10, color, 3)
            result = cv2.line(result, tuple(pt1[0]), (int(pt2[0][0] + 1280.), int(pt2[0][1])), color, 2)

        cv2.namedWindow('Match Points', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Match Points', 1300, 600)
        cv2.imshow('Match Points', result)
        cv2.waitKey(0)

    def __calculate_mean_square_error_hsv(self, left_patch, right_patch):
        height, width, depth = left_patch.shape
        accumulated_error = 0
        for row in range(0, height -1):
            for column in range(0, width - 1):
                accumulated_error += abs(self.round_difference(left_patch[row][column][0], right_patch[row][column][0]))
                accumulated_error += abs(left_patch[row][column][1] - right_patch[row][column][1])
        return accumulated_error / (height * width * 2)

    def round_difference(self, angle1, angle2):
        return 180 - abs(abs(angle1 - angle2) - 180)

    def __match_points_with_epilines(self, points, lines, image1, image2, image2_borders):
        height, width, depth = image2.shape
        points_left = []
        points_right = []
        lines_right = []
        patch_size = 20
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)
        column_range = range(patch_size, width - patch_size)
        epiline_range = range(-1, 1)
        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch_gray(image1, point[0][1], point[0][0], int(patch_size / 2))
            best_mean_square_error = 0.9
            best_point = None

            for column in column_range:
                row = int((-(column * line[0]) - line[2]) / line[1])
                for epiline_offset in epiline_range:
                    if 0 < row < width:
                        if image2_borders[row][column + epiline_offset] == 255:
                            right_patch = self.__get_image_patch_gray(image2, row, column, int(patch_size / 2))
                            if right_patch.shape == (patch_size, patch_size, 3):
                                similarity = cv2.matchTemplate(right_patch, left_patch, cv2.TM_CCORR_NORMED)
                                similarity = similarity[0][0]
                                if similarity > 0.9 and similarity > best_mean_square_error:
                                    best_mean_square_error = similarity
                                    best_point = np.array([[column + epiline_offset, row]], dtype=np.float32)
            if best_point is not None:
                points_left.append(point)
                points_right.append(best_point)
                lines_right.append(line)

        return np.array(points_left), np.array(points_right), np.array(lines_right)

    def __match_similar_interest_points(self, points, points2, lines, image1, image2, image2_borders):
        height, width, depth = image2.shape
        points_left = []
        points_right = []
        lines_right = []
        patch_size = 20
        image1 = cv2.cvtColor(image1, cv2.COLOR_BGR2HSV)
        image2 = cv2.cvtColor(image2, cv2.COLOR_BGR2HSV)

        for line, point in zip(lines, points):
            left_patch = self.__get_image_patch(image1, point[0][1], point[0][0], int(patch_size / 2), int(patch_size / 2))
            best_point = self.__match_points_in_epiline_fast(line, width, left_patch, image2, image2_borders, points2)

            if best_point is not None:
                points_left.append(point)
                points_right.append(best_point)
                lines_right.append(line)

        return np.array(points_left), np.array(points_right), np.array(lines_right)


    def __match_points_in_epiline(self, line, width, left_patch, image_b, border_image_b, points2):
        patch_size = 20
        column_range = range(patch_size, width - patch_size)
        epiline_offset = 1
        similarity_threshold = 0.9
        best_similarity = 0.9
        best_point = None

        limit1 = int((-(0 * line[0]) - line[2]) / line[1])
        limit2 = int((-(points2.shape[0] * line[0]) - line[2]) / line[1])

        for column in column_range:
            row = int((-(column * line[0]) - line[2]) / line[1])
            if 0 < row < width:
                if border_image_b[row][column] == 255:
                    right_patch = self.__get_image_patch(image_b, row, column, int(patch_size / 2), int((patch_size / 2) + (epiline_offset)))
                    if right_patch.shape == (patch_size + 2, patch_size, 3):
                        max_value, max_location = self.__match_column_patch(left_patch, right_patch)
                        if max_value > similarity_threshold and max_value > best_similarity:
                            best_similarity = max_value
                            best_point = np.array([[column + (max_location[1] - 1), row]], dtype=np.float32)
        return best_point

    def __match_points_in_epiline_fast(self, line, width, left_patch, image_b, border_image_b, points2):
        patch_size = 20
        column_range = range(patch_size, width - patch_size)
        epiline_offset = 1
        similarity_threshold = 0.9
        best_similarity = 0.9
        best_point = None

        limits = [
            int((-(0 * line[0]) - line[2]) / line[1]),
            int((-(points2.shape[0] * line[0]) - line[2]) / line[1])
        ]
        limits.sort()

        relevant_points = points2[limits[0]:limits[1]]

        print(limits[0], limits[1])
        for columns, row_number in zip(relevant_points, range(limits[0], limits[1])):
            print(row_number)
            for column in columns:
                if 0 == int((row_number * line[0]) + column * line[1] + line[2]):
                    if 0 < row_number < width:
                        right_patch = self.__get_image_patch(image_b, row_number, column, int(patch_size / 2),
                                                             int((patch_size / 2) + (epiline_offset)))
                        if right_patch.shape == (patch_size + 2, patch_size, 3):
                            max_value, max_location = self.__match_column_patch(left_patch, right_patch)
                            if max_value > similarity_threshold and max_value > best_similarity:
                                best_similarity = max_value
                                best_point = np.array([[column + (max_location[1] - 1), row_number]], dtype=np.float32)
        return best_point

    def __match_column_patch(self, needle, haystack):
        similarities = cv2.matchTemplate(haystack, needle, cv2.TM_CCORR_NORMED)
        __, maxVal, __, maxLoc = cv2.minMaxLoc(similarities)
        return maxVal, maxLoc

    def __get_image_patch(self, image, position_x, position_y, height, width, depth = 1):
        return image[position_x-width:position_x+width, position_y-height:position_y+height, :]
