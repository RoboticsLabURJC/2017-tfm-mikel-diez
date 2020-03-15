import cv2
import numpy as np
import cProfile

from src.vision.matching.domain.value_objects.interest_points_value_object import InterestPointsValueObject


class MatchInterestPointsWithBRIEF:
    def __init__(self, stereo_calibration):
        self.stereo_calibration = stereo_calibration
        self.feature_detector = cv2.BRIEF_create()

    def execute(self, image_a, image_b):
        image_a_points_of_interest = InterestPointsValueObject(image_a, 10)
        image_b_points_of_interest = InterestPointsValueObject(image_b)

        epilines_a = cv2.computeCorrespondEpilines(image_a_points_of_interest.get_interest_points(), 1, self.stereo_calibration['F'])
        epilines_a = epilines_a.reshape(-1, 3)

        pr = cProfile.Profile()
        pr.enable()
        points_left, points_right = self.__get_matched_points_by_epiline(
            image_a_points_of_interest.get_interest_points(),
            image_b_points_of_interest,
            epilines_a,
            image_a,
            image_b
        )

        pr.disable()
        pr.print_stats()

        return points_left, points_right

    def __get_matched_points_by_epiline(self, points_a, image_b_points_of_interest, lines, image_a, image_b):
        points_left = []
        points_right = []

        for line, point in zip(lines, points_a):
            new_array, interest_points_in_range = image_b_points_of_interest.get_interest_points_in_line(line)
            if np.where(new_array == 0)[0].size is not 0:
                interest_points_in_line = np.unique(interest_points_in_range[np.where(new_array == 0)[0]], axis=0)

                # Compute Feeature
                key_point_1 = [cv2.KeyPoint(x[0][0], x[0][1], 1) for x in np.array([[[point[0][0], point[0][1]]]], dtype=np.float32)]
                key_points_in_line = [cv2.KeyPoint(x[0][0], x[0][1], 1) for x in interest_points_in_line]

                key_points_1, descriptors_1 = self.feature_detector.compute(image_a, np.array(key_point_1))
                key_points_2, descriptors_2 = self.feature_detector.compute(image_b, key_points_in_line)

                # Brute Force Matching
                if descriptors_1 is not None and descriptors_2 is not None:
                    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
                    matches = bf.match(descriptors_1, descriptors_2)
                    matches = sorted(matches, key=lambda x: x.distance)

                    if matches[0].distance < 800.0:
                        points_left.append(np.array([[key_point_1[0].pt[0], key_point_1[0].pt[1]]]))
                        points_right.append(np.array([[key_points_2[matches[0].trainIdx].pt[0], key_points_2[matches[0].trainIdx].pt[1]]]))

        return np.array(points_left), np.array(points_right)
