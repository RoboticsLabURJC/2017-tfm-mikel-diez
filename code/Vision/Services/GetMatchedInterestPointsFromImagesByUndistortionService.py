import cv2
import numpy as np
import logging
import cProfile
from Vision.Components.GUI.Helpers import imShowTwoImages
from datetime import datetime

class GetMatchedInterestPointsFromImagesByUndistortionService:
    def __init__(self, stereo_calibration, camera_a_calibration, camera_b_calibration):
        self.stereo_calibration = stereo_calibration
        self.camera_a_calibration = camera_a_calibration
        self.camera_b_calibration = camera_b_calibration

    def execute(self, image_a, image_b):
        image_a_borders = self.__get_border_image(image_a)
        image_b_borders = self.__get_border_image(image_b)

        R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(
            self.stereo_calibration["cameraMatrix1"],
            self.stereo_calibration["distCoeffs1"],
            self.stereo_calibration["cameraMatrix2"],
            self.stereo_calibration["distCoeffs2"], (960, 540),
            self.stereo_calibration["R"],
            self.stereo_calibration["T"],
            alpha=0
        )

        left_maps = cv2.initUndistortRectifyMap(
            self.stereo_calibration["cameraMatrix1"],
            self.stereo_calibration["distCoeffs1"],
            R1,
            P1,
            (960, 540),
            cv2.CV_16SC2
        )
        right_maps = cv2.initUndistortRectifyMap(
            self.stereo_calibration["cameraMatrix2"],
            self.stereo_calibration["distCoeffs2"],
            R2,
            P2,
            (960, 540),
            cv2.CV_16SC2
        )

        image_a_undistorted = cv2.remap(image_a, left_maps[0], left_maps[1], cv2.INTER_LANCZOS4)
        image_b_undistorted = cv2.remap(image_b, right_maps[0], right_maps[1], cv2.INTER_LANCZOS4)

        imShowTwoImages(image_a_undistorted, image_b_undistorted, 'Ale')
        cv2.waitKey(0)

        win_size = 5
        min_disp = -1
        max_disp = 15  # min_disp * 9
        num_disp = max_disp - min_disp  # Needs to be divisible by 16

        # Create Block matching object.
        stereo = cv2.StereoSGBM_create(
            minDisparity=min_disp,
            numDisparities=num_disp,
            blockSize=5,
            uniquenessRatio=5,
            speckleWindowSize=5,
            speckleRange=5,
            disp12MaxDiff=1,
            P1=8 * 3 * win_size ** 2,  # 8*3*win_size**2,
            P2=32 * 3 * win_size ** 2)  # 32*3*win_size**2)
        dispmap_sgbm = stereo.compute(image_a_undistorted, image_b_undistorted)
        disparity = dispmap_sgbm.astype(np.float32) / (16.0 * 32)
        print(disparity)
        cv2.imshow('image', disparity)
        cv2.waitKey(0)

        points_3D = cv2.reprojectImageTo3D(dispmap_sgbm, Q)

        colors = cv2.cvtColor(image_a, cv2.COLOR_BGR2RGB)
        mask_map = dispmap_sgbm > dispmap_sgbm.min()

        output_points = points_3D[mask_map]
        output_colors = colors[mask_map]

        output_file = 'reconstructed.ply'

        self.create_output(output_points, output_colors, output_file)

        image_a_undistorted_sampled = self.__remove_points(image_a_undistorted, 5)

        interest_points_a = np.array(cv2.findNonZero(image_a_undistorted_sampled), dtype=np.float32)
        interest_points_b = self.get_right_points_structure(image_b_undistorted)

        logging.info('[{}] Start Match Points With Template'.format(datetime.now().time()))
        pr = cProfile.Profile()
        pr.enable()
        left_points, right_points = self.__get_interest_points_matched(interest_points_a, image_b_undistorted, image_a, image_b)
        print(left_points.shape)
        print(right_points.shape)
        pr.disable()
        pr.print_stats()

        logging.info('[{}] End Match Points With Template'.format(datetime.now().time()))
        logging.info('[{}] Points to be Matched'.format(interest_points_a.shape[0]))
        logging.info('[{}] Points Matched'.format(left_points.shape[0]))

        return left_points, right_points

    @staticmethod
    def create_output(vertices, colors, filename):
        colors = colors.reshape(-1, 3)
        vertices = np.hstack([vertices.reshape(-1, 3), colors])

        ply_header = '''ply
    		format ascii 1.0
    		element vertex %(vert_num)d
    		property float x
    		property float y
    		property float z
    		property uchar red
    		property uchar green
    		property uchar blue
    		end_header
    		'''
        with open(filename, 'w') as f:
            f.write(ply_header % dict(vert_num=len(vertices)))

            np.savetxt(f, vertices, '%f %f %f %d %d %d')

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
        non_zero_pixels_structure = np.empty((border_image.shape[0],), dtype=object)
        non_zero_pixels_structure[...] = [[] for _ in range(border_image.shape[0])]
        non_zero_pixels = np.array(cv2.findNonZero(border_image), dtype=np.float32)
        for non_zero_pixel in non_zero_pixels:
            non_zero_pixels_structure[non_zero_pixel[0][1]].append(non_zero_pixel[0][0])
        return non_zero_pixels_structure

    def __get_interest_points_matched(self, interest_points_a, image_b_borders, image_a, image_b):
        height, width, depth = image_a.shape
        points_left = []
        points_right = []
        patch_size = 20
        image1 = cv2.cvtColor(image_a, cv2.COLOR_BGR2HSV)
        image2 = cv2.cvtColor(image_b, cv2.COLOR_BGR2HSV)
        column_range = range(patch_size, width - patch_size)
        epiline_range = range(-1, 1)
        for interest_point_a in interest_points_a:
            left_patch = self.__get_image_patch(image1, interest_point_a[0][1], interest_point_a[0][0], int(patch_size / 2), int(patch_size / 2))
            best_mean_square_error = 0.9
            best_point = None

            for column in column_range:
                for epiline_offset in epiline_range:
                    if 0 < interest_point_a[0][1] < width:
                        if image_b_borders[interest_point_a[0][1]][column + epiline_offset] == 255:
                            right_patch = self.__get_image_patch(image2, interest_point_a[0][1], column, int(patch_size / 2), int(patch_size / 2))
                            if right_patch.shape == (patch_size, patch_size, 3):
                                similarity = cv2.matchTemplate(right_patch, left_patch, cv2.TM_CCORR_NORMED)
                                similarity = similarity[0][0]
                                if similarity > 0.9 and similarity > best_mean_square_error:
                                    best_mean_square_error = similarity
                                    best_point = np.array([[column + epiline_offset, interest_point_a[0][1]]], dtype=np.float32)
            if best_point is not None:
                points_left.append(interest_point_a)
                points_right.append(best_point)

        return np.array(points_left), np.array(points_right)

    @staticmethod
    def __match_column_patch(needle, haystack):
        similarities = cv2.matchTemplate(haystack, needle, cv2.TM_CCORR_NORMED)
        __, maxVal, __, maxLoc = cv2.minMaxLoc(similarities)
        return maxVal, maxLoc

    @staticmethod
    def __get_image_patch(image, position_x, position_y, height, width, depth = 1):
        return image[position_x-width:position_x+width, position_y-height:position_y+height, :]
