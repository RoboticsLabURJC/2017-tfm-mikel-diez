import os
import numpy as np
import cv2
import glob
import yaml
import math
import copy


class CalibrateStereoCamerasFromChessboard:
    STOP_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    PATTERN_SIZE = (8, 6)
    IMAGE_FORMAT = '.png'

    def __init__(self):
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        self.objp = np.zeros((self.PATTERN_SIZE[1] * self.PATTERN_SIZE[0], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.PATTERN_SIZE[0], 0:self.PATTERN_SIZE[1]].T.reshape(-1, 2)
        self.objp *= 28

        # Arrays to store object points and image points from all the images.
        self.objpoints = []  # 3d point in real world space
        self.imgpoints_left = []  # 2d points in image plane.
        self.imgpoints_right = []  # 2d points in image plane.
        self.image_size = []
        self.gray_images_shape = []

    def execute(self, image_set):
        images_left = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/left*' + self.IMAGE_FORMAT))
        images_right = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/right*' + self.IMAGE_FORMAT))

        self.matrix_width = math.ceil(math.sqrt(len(images_left)))
        self.matrix_height = math.ceil(len(images_left) / self.matrix_width)

        self.extract_chessboard_points(images_left, images_right)



        E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2 = self.stereo_calibration()

        # Save the calibration matrix in a yaml file.
        if not os.path.exists('bin/sets/' + image_set):
            os.makedirs('bin/sets/' + image_set)
        with open('bin/sets/' + image_set + '/calibrated_camera.yml', 'w') as outfile:
            yaml.dump(
                {
                    'stereocalib_retval': stereocalib_retval,
                    'cameraMatrix1': cameraMatrix1,
                    'distCoeffs1': distCoeffs1,
                    'cameraMatrix2': cameraMatrix2,
                    'distCoeffs2': distCoeffs2,
                    'R': R,
                    'T': T,
                    'E': E,
                    'F': F,
                    'rvecs1': rvecs1,
                    'rvecs2': rvecs2,
                    'tvecs1': tvecs1,
                    'tvecs2': tvecs2
                },
                outfile,
                default_flow_style=False)

        # Check the error of the meassure
        tot_error = 0
        for i in xrange(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs1[i], tvecs1[i], cameraMatrix1, distCoeffs1)
            error = cv2.norm(self.imgpoints_left[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            tot_error += error
        print("total error left: ", tot_error / len(self.objpoints))
        for i in xrange(len(self.objpoints)):
            imgpoints2, _ = cv2.projectPoints(self.objpoints[i], rvecs2[i], tvecs2[i], cameraMatrix2, distCoeffs2)
            error = cv2.norm(self.imgpoints_right[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            tot_error += error
        print("total error right: ", tot_error / len(self.objpoints))
        print('ret1; ', ret1)
        print('ret2: ', ret2)
        print('retval: ', stereocalib_retval)

    def stereo_calibration(self):
        # Calibrate cameras individualy
        ret1, cameraMatrix1, distCoeffs1, rvecs1, tvecs1 = cv2.calibrateCamera(self.objpoints, self.imgpoints_left,
                                                                               self.gray_images_shape[::-1], None, None)
        ret2, cameraMatrix2, distCoeffs2, rvecs2, tvecs2 = cv2.calibrateCamera(self.objpoints, self.imgpoints_right,
                                                                               self.gray_images_shape[::-1], None, None)

        # Calibrate stereo camera
        stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
        stereocalib_flags = cv2.CALIB_FIX_INTRINSIC
        stereocalib_retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
            self.objpoints, self.imgpoints_left, self.imgpoints_right, cameraMatrix1, distCoeffs1, cameraMatrix2,
            distCoeffs2,
            self.gray_images_shape[::-1], criteria=stereocalib_criteria, flags=stereocalib_flags)

        return E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2

    def extract_chessboard_points(self, images_left, images_right):
        self.images_with_corners_left = np.zeros((int(720 * self.matrix_height), int(1280 * self.matrix_width), 3), np.uint8)
        self.images_with_corners_right = np.zeros((int(720 * self.matrix_height), int(1280 * self.matrix_width), 3), np.uint8)

        for index, file_name in enumerate(images_left):
            # Load images and convert to gray
            img_left = cv2.imread(file_name)
            gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
            img_right = cv2.imread(images_right[index])
            gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

            self.gray_images_shape = gray_left.shape
            # Find the chess board corners in both images
            left_found, left_corners = cv2.findChessboardCorners(gray_left, self.PATTERN_SIZE,
                                                                 cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)
            right_found, right_corners = cv2.findChessboardCorners(gray_right, self.PATTERN_SIZE,
                                                                   cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)

            # If found, add object points, image points (after refining them)
            if left_found and right_found:
                left_corners = cv2.cornerSubPix(gray_left, left_corners, (11, 11), (-1, -1), self.STOP_CRITERIA)
                right_corners = cv2.cornerSubPix(gray_right, right_corners, (11, 11), (-1, -1), self.STOP_CRITERIA)

                self.objpoints.append(self.objp)
                self.imgpoints_left.append(left_corners)
                self.imgpoints_right.append(right_corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img_left, self.PATTERN_SIZE, left_corners, left_found)
            cv2.drawChessboardCorners(img_right, self.PATTERN_SIZE, right_corners, right_found)

            cv2.imshow('image_a', img_left)
            cv2.waitKey(0)

            x = int(math.floor(index / self.matrix_width))
            y = int(index - (self.matrix_width * x))

            self.images_with_corners_left[720 * x: 720 * (x + 1), 1280 * y:1280 * (y + 1), :] = img_left
            self.images_with_corners_right[720 * x: 720 * (x + 1), 1280 * y:1280 * (y + 1), :] = img_right
