import cv2
import yaml
import numpy as np

from Vision.Services.Matching.GetImageKeyPoints import GetImageKeyPoints
from Vision.Services.Matching.MatchInterestPointsWithOrb import MatchInterestPointsWithOrb



def __remove_points(image, patch_size=40):
    height, width = image.shape
    result = np.zeros((height, width), np.uint8)
    for row in range(10 + patch_size, height - (10 + patch_size)):
        for column in range(10 + patch_size, width - (10 + patch_size)):
            if image[row][column] == 255:
                result[row][column] = 255
                image[row - patch_size:row + patch_size, column - patch_size:column + patch_size] = 0

    return result


def __get_image_patch(image, position_x, position_y, height, width, depth = 1):
    return image[int(position_x-width):int(position_x+width), int(position_y-height):int(position_y+height), :]


if __name__ == '__main__':
    image_a = cv2.imread('bin/sets/set_10y_center/images/left_image_1.png')
    image_b = cv2.imread('bin/sets/set_10y_center/images/right_image_1.png')

    point_a = np.array([[[1091, 331]]], dtype=np.float32)
    point_b = np.array([[[705, 437]]], dtype=np.float32)

    with open("bin/sets/set_10y_center/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream, Loader=yaml.UnsafeLoader)

            gray_a = cv2.cvtColor(image_a, cv2.COLOR_BGR2GRAY)
            gray_b = cv2.cvtColor(image_b, cv2.COLOR_BGR2GRAY)

            borders_a = cv2.Canny(image_a, 100, 200)
            borders_a = __remove_points(borders_a, 20)
            borders_b = cv2.Canny(image_b, 100, 200)

            width = image_a.shape[1]
            height = image_a.shape[0]

            print('width', width)
            print('height', height)


            get_image_key_points_1 = GetImageKeyPoints()
            key_points_1, descriptors_1, non_zero_pixels_1, non_zero_pixels_by_row_1 = get_image_key_points_1.execute(image_a, borders_a)
            get_image_key_points_2 = GetImageKeyPoints()
            key_points_2, descriptors_2, non_zero_pixels_2, non_zero_pixels_by_row_2 = get_image_key_points_2.execute(image_b, borders_b)

            epilines = cv2.computeCorrespondEpilines(point_a, 1, data['F'])
            epilines = epilines.reshape(-1, 3)

            # img2 = cv2.drawKeypoints(image_b, key_points_2, None, color=(0, 255, 0), flags=0)
            # cv2.imshow('computed', img2)
            # cv2.waitKey(0)
            #
            # img2 = cv2.drawKeypoints(image_a, key_points_1, None, color=(0, 255, 0), flags=0)
            # cv2.imshow('computed', img2)
            # cv2.waitKey(0)

            non_zero_pixels = np.array(cv2.findNonZero(borders_b), dtype=np.float32)
            non_zero_pixels_by_row = borders_b.sum(axis=1) / 255
            non_zero_pixels_index = np.cumsum(non_zero_pixels_by_row)

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

            print(limits)
            print(non_zero_pixels_index)
            print(interest_points_in_range)

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
            matching_result = cv2.drawMatches(image_a, key_points_1, image_b, key_points_2, matches[:50], None, flags=2)

            cv2.imshow("Matching result", matching_result)
            cv2.waitKey(0)

            cv2.destroyAllWindows()

        except yaml.YAMLError as exc:
            print(exc)





