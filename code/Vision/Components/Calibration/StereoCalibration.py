import os
import numpy as np
import cv2
import glob
import yaml
import sys


class StereoCalibration:

    def __init__(self):
        print("Stereo Calibration Activated")
        self.stop_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.pattern_size = (8, 6)
        self.images_format = '.png'

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        self.objp = np.zeros((self.pattern_size[1] * self.pattern_size[0], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.pattern_size[0], 0:self.pattern_size[1]].T.reshape(-1, 2)

        # Arrays to store object points and image points from all the images.
        self.objpoints = []  # 3d point in real world space
        self.imgpoints_left = []  # 2d points in image plane.
        self.imgpoints_right = []  # 2d points in image plane.
        self.image_size = []
        self.gray_images_shape = []

    def calibrate_set(self, image_set):
        images_left = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/left*' + self.images_format))
        images_right = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/right*' + self.images_format))

        for index, file_name in enumerate(images_left):
            # Load images and convert to gray
            img_left = cv2.imread(file_name)
            gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
            img_right = cv2.imread(images_right[index])
            gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

            image_size = img_left.shape
            self.gray_images_shape = gray_left.shape
            # Find the chess board corners in both images
            left_found, left_corners = cv2.findChessboardCorners(gray_left, self.pattern_size,
                                                                 cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)
            right_found, right_corners = cv2.findChessboardCorners(gray_right, self.pattern_size,
                                                                   cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)

            if left_found:
                cv2.cornerSubPix(gray_left, left_corners, (11, 11), (-1, -1), self.stop_criteria)
            if right_found:
                cv2.cornerSubPix(gray_right, right_corners, (11, 11), (-1, -1), self.stop_criteria)

            # If found, add object points, image points (after refining them)
            if left_found and right_found:
                self.objpoints.append(self.objp)
                self.imgpoints_left.append(left_corners)
                self.imgpoints_right.append(right_corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img_left, self.pattern_size, left_corners, left_found)
            cv2.drawChessboardCorners(img_right, self.pattern_size, right_corners, right_found)
            cv2.namedWindow('Left Image', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('Left Image', 700, 400)
            cv2.imshow('Left Image', img_left)
            cv2.waitKey(500)

        # Destroy windows
        cv2.destroyAllWindows()

        print(self.gray_images_shape)

        # Calibrate cameras individualy
        ret1, cameraMatrix1, distCoeffs1, rvecs1, tvecs1 = cv2.calibrateCamera(self.objpoints, self.imgpoints_left, self.gray_images_shape[::-1], None, None)
        ret2, cameraMatrix2, distCoeffs2, rvecs2, tvecs2 = cv2.calibrateCamera(self.objpoints, self.imgpoints_right,
                                                                               self.gray_images_shape[::-1], None, None)

        # Calibrate stereo camera
        stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
        # stereocalib_flags = cv2.CALIB_FIX_ASPECT_RATIO | cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K3 | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5

        stereocalib_flags = cv2.CALIB_FIX_INTRINSIC
        stereocalib_retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
            self.objpoints, self.imgpoints_left, self.imgpoints_right, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2,
            gray_left.shape[::-1], criteria=stereocalib_criteria, flags=stereocalib_flags)

        # Save the calibration matrix in a yaml file.
        if not os.path.exists('bin/sets/' + image_set):
            os.makedirs('bin/sets/' + image_set)
        with open('bin/sets/' + image_set + '/calibrated_camera.yml', 'w') as outfile:
            yaml.dump(
                {'stereocalib_retval': stereocalib_retval, 'cameraMatrix1': cameraMatrix1, 'distCoeffs1': distCoeffs1,
                 'cameraMatrix2': cameraMatrix2, 'distCoeffs2': distCoeffs2, 'R': R, 'T': T, 'E': E, 'F': F}, outfile,
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