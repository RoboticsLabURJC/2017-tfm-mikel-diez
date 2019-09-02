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
    IMAGES_SHAPE = (720, 1280)

    def __init__(self):
        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        self.objp = np.zeros((self.PATTERN_SIZE[1] * self.PATTERN_SIZE[0], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.PATTERN_SIZE[0], 0:self.PATTERN_SIZE[1]].T.reshape(-1, 2)
        self.objp *= 28

    def execute(self, image_set):
        images_left = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/left*' + self.IMAGE_FORMAT))
        images_right = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/right*' + self.IMAGE_FORMAT))

        self.matrix_width = math.ceil(math.sqrt(len(images_left)))
        self.matrix_height = math.ceil(len(images_left) / self.matrix_width)

        object_points, image_points_a, image_points_b = self.extract_chessboard_points(images_left, images_right)



        E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2 = self.stereo_calibration(object_points, image_points_a, image_points_b)

        self.saveStereoCalibrationData(E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, image_set,
                                       rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2)

        self.checkBackprojectError(cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2,
                                   stereocalib_retval, tvecs1, tvecs2, object_points, image_points_a, image_points_b)

    def checkBackprojectError(self, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2,
                              stereocalib_retval, tvecs1, tvecs2, object_points, image_points_a, image_points_b):
        total_error_a = 0
        total_error_b = 0
        for i in xrange(len(object_points)):
            imgpoints2, _ = cv2.projectPoints(object_points[i], rvecs1[i], tvecs1[i], cameraMatrix1, distCoeffs1)
            error = cv2.norm(image_points_a[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            total_error_a += error
        print("total error left: ", total_error_a / len(object_points))
        for i in xrange(len(object_points)):
            imgpoints2, _ = cv2.projectPoints(object_points[i], rvecs2[i], tvecs2[i], cameraMatrix2, distCoeffs2)
            error = cv2.norm(image_points_b[i], imgpoints2, cv2.NORM_L2) / len(imgpoints2)
            total_error_b += error
        print("total error right: ", total_error_b / len(object_points))
        print('ret1; ', ret1)
        print('ret2: ', ret2)
        print('retval: ', stereocalib_retval)

    def saveStereoCalibrationData(self, E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, image_set,
                                  rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2):
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

    def stereo_calibration(self, object_points, image_points_a, image_points_b):
        # Calibrate cameras individualy
        ret1, camera_matrix_a, distortion_coefficients_a, rvecs1, tvecs1 = cv2.calibrateCamera(object_points, image_points_a,
                                                                               self.IMAGES_SHAPE[::-1], None, None)
        ret2, camera_matrix_b, distortion_coefficients_b, rvecs2, tvecs2 = cv2.calibrateCamera(object_points, image_points_b,
                                                                               self.IMAGES_SHAPE[::-1], None, None)

        # Calibrate stereo camera
        stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
        stereocalib_flags = cv2.CALIB_FIX_INTRINSIC
        stereocalib_retval, camera_matrix_a, distortion_coefficients_a, camera_matrix_b, distortion_coefficients_b, R, T, E, F = cv2.stereoCalibrate(
            object_points,
            image_points_a,
            image_points_b,
            camera_matrix_a,
            distortion_coefficients_a,
            camera_matrix_b,
            distortion_coefficients_b,
            self.IMAGES_SHAPE[::-1],
            criteria=stereocalib_criteria,
            flags=stereocalib_flags
        )

        return E, F, R, T, camera_matrix_a, camera_matrix_b, distortion_coefficients_a, distortion_coefficients_b, ret1, ret2, rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2

    def extract_chessboard_points(self, images_a_paths, images_b_paths):
        object_points = []
        image_points_a = []
        image_points_b = []

        for image_a_path, image_b_path in zip(images_a_paths, images_b_paths):

            image_a_gray, image_b_gray = self.get_gray_images_from_path(image_a_path, image_b_path)

            corners_in_image_a_found, image_a_corners = cv2.findChessboardCorners(
                image_a_gray,
                self.PATTERN_SIZE,
                cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK
            )
            corners_in_image_b_found, image_b_corners = cv2.findChessboardCorners(
                image_b_gray,
                self.PATTERN_SIZE,
                cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK
            )

            if corners_in_image_a_found and corners_in_image_b_found:
                image_a_corners = cv2.cornerSubPix(image_a_gray, image_a_corners, (11, 11), (-1, -1), self.STOP_CRITERIA)
                image_b_corners = cv2.cornerSubPix(image_b_gray, image_b_corners, (11, 11), (-1, -1), self.STOP_CRITERIA)

                object_points.append(self.objp)
                image_points_a.append(image_a_corners)
                image_points_b.append(image_b_corners)

            #self.diplayChessboardWithCorners(img_left, img_right, image_b_corners, corners_in_image_a_found, image_b_corners, corners_in_image_b_found)

        return object_points, image_points_a, image_points_b

    def get_gray_images_from_path(self, image_a_path, image_b_path):
        img_left = cv2.imread(image_a_path)
        gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
        img_right = cv2.imread(image_b_path)
        gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)
        return gray_left, gray_right

    def diplayChessboardWithCorners(self, img_left, img_right, left_corners, left_found, right_corners, right_found):
        # Draw and display the corners
        cv2.drawChessboardCorners(img_left, self.PATTERN_SIZE, left_corners, left_found)
        cv2.drawChessboardCorners(img_right, self.PATTERN_SIZE, right_corners, right_found)
        cv2.imshow('image_a', img_left)
        cv2.waitKey(0)
