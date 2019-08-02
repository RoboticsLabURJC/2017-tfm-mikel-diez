import cv2
import numpy as np
import yaml
import cProfile
from Vision.ValueObjects.InterestPointsValueObject import InterestPointsValueObject

if __name__ == '__main__':
    image_a = cv2.imread('bin/sets/set_10y_center/images/left_image_1.png')
    image_b = cv2.imread('bin/sets/set_10y_center/images/right_image_1.png')

    point_a = np.array([[[1091, 331]]], dtype=np.float32)
    point_b = np.array([[[705, 437]]], dtype=np.float32)

    with open("bin/sets/set_10y_center/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream, Loader=yaml.UnsafeLoader)

            image_a_points_of_interest = InterestPointsValueObject(image_a, 20)
            image_b_points_of_interest = InterestPointsValueObject(image_b)




            ###### Dirt

            non_zero_pixels = image_b_points_of_interest.get_interest_points()
            non_zero_pixels_index = image_b_points_of_interest.get_interest_points_row_index()

            width = image_a.shape[1]
            height = image_a.shape[0]

            epilines = cv2.computeCorrespondEpilines(point_a, 1, data['F'])
            epilines = epilines.reshape(-1, 3)

            #######
            left_keypoint = [cv2.KeyPoint(x[0][0], x[0][1], 1) for x in point_a]

            limits = [
                int((-(0 * epilines[0][0]) - epilines[0][2]) / epilines[0][1]),
                int((-(width * epilines[0][0]) - epilines[0][2]) / epilines[0][1])
            ]
            limits[1] = limits[1] if limits[1] < image_a.shape[0] - 1 else image_a.shape[0] - 1
            limits[0] = limits[0] if limits[0] < image_a.shape[0] - 1 else image_a.shape[0] - 1
            limits.sort()

            interest_points_in_range = non_zero_pixels[non_zero_pixels_index[limits[0] - 1]:non_zero_pixels_index[limits[1]]]

            line_function = np.array([
                [-epilines[0][0] / epilines[0][1]],
                [-1]
            ])

            new_array = np.dot(interest_points_in_range, line_function) - (epilines[0][2] / epilines[0][1])
            new_array = new_array.astype(int)

            if np.where(new_array == 0)[0].size is not 0:
                interest_points_in_line = np.unique(interest_points_in_range[np.where(new_array == 0)[0]], axis=0)

                key_points_in_line = [cv2.KeyPoint(x[0][0], x[0][1], 1) for x in interest_points_in_line]

            #######
            print(point_a)
            print(left_keypoint[0].pt)
            print(key_points_in_line[0].pt)
            img2 = cv2.drawKeypoints(image_b, key_points_in_line, None, color=(0, 255, 0), flags=0)
            cv2.imshow('computed', img2)
            cv2.waitKey(0)

            orb_detector = cv2.ORB_create()
            key_points_1, descriptors_1 = orb_detector.compute(image_a, np.array(left_keypoint))
            key_points_2, descriptors_2 = orb_detector.compute(image_b, key_points_in_line)


            # Brute Force Matching
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = bf.match(descriptors_1, descriptors_2)
            matches = sorted(matches, key=lambda x: x.distance)
            print(matches[0].queryIdx)
            print(matches[0].trainIdx)
            print(key_points_2[matches[0].queryIdx].pt)
            print(key_points_2[matches[0].trainIdx].pt)
            matching_result = cv2.drawMatches(image_a, key_points_1, image_b, key_points_2, matches[:10], None, flags=2)
            cv2.imshow('matches', image_b)
            cv2.waitKey(0)

        except yaml.YAMLError as exc:
            print(exc)
