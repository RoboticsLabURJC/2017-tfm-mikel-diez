import os
import numpy as np
import cv2
import glob
import yaml
import math


class StereoCalibrationFromChessboard:
    def __init__(self):
        print("Stereo Calibration Activated")
        self.stop_criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)
        self.pattern_size = (8, 6)
        self.images_format = '.png'

        # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
        self.objp = np.zeros((self.pattern_size[1] * self.pattern_size[0], 3), np.float32)
        self.objp[:, :2] = np.mgrid[0:self.pattern_size[0], 0:self.pattern_size[1]].T.reshape(-1, 2)
        self.objp *= 28

        # Arrays to store object points and image points from all the images.
        self.objpoints = []  # 3d point in real world space
        self.imgpoints_left = []  # 2d points in image plane.
        self.imgpoints_right = []  # 2d points in image plane.
        self.image_size = []
        self.gray_images_shape = []

    def execute(self, image_set):
        images_left = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/left*' + self.images_format))
        images_right = sorted(glob.glob('bin/sets/' + image_set + '/calibration_images/right*' + self.images_format))

        self.matrix_width = math.ceil(math.sqrt(len(images_left)))
        self.matrix_height = math.ceil(len(images_left) / self.matrix_width)
        print(self.matrix_width)
        print(self.matrix_height)

        self.extract_chessboard_points(images_left, images_right)

        #cv2.imshow('Cornered Images Left', self.images_with_corners_left)
        #cv2.imshow('Cornered Images Right', self.images_with_corners_right)
        #cv2.waitKey(0)

        E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2 = self.stereo_calibration()

        print(R)
        print(T)

        rectify_scale = 1  # 0=full crop, 1=no crop
        r1, r2, p1, p2, q, roi1, roi2 = cv2.stereoRectify(
            cameraMatrix1,
            distCoeffs1,
            cameraMatrix2,
            distCoeffs2,
            self.gray_images_shape[::-1],
            R,
            T,
            alpha=rectify_scale
        )

        individualCameraMatrix, rotMatrix, transVect, rotMatrixX, rotMatrixY, rotMatrixZ, eulerAngles = cv2.decomposeProjectionMatrix(
            p1,
            cameraMatrix1
        )
        individualCameraMatrix2, rotMatrix2, transVect2, rotMatrixX2, rotMatrixY2, rotMatrixZ2, eulerAngles2 = cv2.decomposeProjectionMatrix(
            p2,
            cameraMatrix2
        )

        euler_x, euler_y, euler_z = self.calculate_euler_angles_from_rotation_matrix(R)

        print(euler_x, euler_y, euler_z)

        # Save the calibration matrix in a yaml file.
        if not os.path.exists('bin/sets/' + image_set):
            os.makedirs('bin/sets/' + image_set)
        with open('bin/sets/' + image_set + '/calibrated_camera.yml', 'w') as outfile:
            print(image_set)
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
                    'r1': r1,
                    'r2': r2,
                    'p1': p1,
                    'p2': p2,
                    'q': q,
                    'roi1': roi1,
                    'roi2': roi2
                },
                outfile,
                default_flow_style=False)

        with open('bin/sets/' + image_set + '/camera_A_calibration.yml', 'w') as outfile:
            yaml.dump(
                {
                    'cameraMatrix': individualCameraMatrix,
                    'rotationMatrix': rotMatrix,
                    'translationVector': transVect,
                    'rotMatrixX': rotMatrixX,
                    'rotMatrixY': rotMatrixY,
                    'rotMatrixZ': rotMatrixZ,
                    'eulerAngles': eulerAngles
                }, outfile,
                default_flow_style=False)

        with open('bin/sets/' + image_set + '/camera_B_calibration.yml', 'w') as outfile:
            yaml.dump(
                {
                    'cameraMatrix': individualCameraMatrix2,
                    'rotationMatrix': rotMatrix2,
                    'translationVector': transVect2,
                    'rotMatrixX': rotMatrixX2,
                    'rotMatrixY': rotMatrixY2,
                    'rotMatrixZ': rotMatrixZ2,
                    'eulerAngles': eulerAngles2
                }, outfile,
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
        # stereocalib_flags = cv2.CALIB_FIX_ASPECT_RATIO | cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K3 | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5
        stereocalib_flags = cv2.CALIB_FIX_INTRINSIC
        stereocalib_retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(
            self.objpoints, self.imgpoints_left, self.imgpoints_right, cameraMatrix1, distCoeffs1, cameraMatrix2,
            distCoeffs2,
            self.gray_images_shape[::-1], criteria=stereocalib_criteria, flags=stereocalib_flags)
        return E, F, R, T, cameraMatrix1, cameraMatrix2, distCoeffs1, distCoeffs2, ret1, ret2, rvecs1, rvecs2, stereocalib_retval, tvecs1, tvecs2

    def extract_chessboard_points(self, images_left, images_right):
        self.images_with_corners_left = np.zeros((int(720 * self.matrix_height), int(1280 * self.matrix_width), 3), np.uint8)
        self.images_with_corners_right = np.zeros((int(720 * self.matrix_height), int(1280 * self.matrix_width), 3),
                                                 np.uint8)
        for index, file_name in enumerate(images_left):
            # Load images and convert to gray
            img_left = cv2.imread(file_name)
            gray_left = cv2.cvtColor(img_left, cv2.COLOR_BGR2GRAY)
            img_right = cv2.imread(images_right[index])
            gray_right = cv2.cvtColor(img_right, cv2.COLOR_BGR2GRAY)

            self.gray_images_shape = gray_left.shape
            # Find the chess board corners in both images
            left_found, left_corners = cv2.findChessboardCorners(gray_left, self.pattern_size,
                                                                 cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)
            right_found, right_corners = cv2.findChessboardCorners(gray_right, self.pattern_size,
                                                                   cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)

            # If found, add object points, image points (after refining them)
            if left_found and right_found:
                left_corners = cv2.cornerSubPix(gray_left, left_corners, (11, 11), (-1, -1), self.stop_criteria)
                right_corners = cv2.cornerSubPix(gray_right, right_corners, (11, 11), (-1, -1), self.stop_criteria)

                self.objpoints.append(self.objp)
                self.imgpoints_left.append(left_corners)
                self.imgpoints_right.append(right_corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img_left, self.pattern_size, left_corners, left_found)
            cv2.drawChessboardCorners(img_right, self.pattern_size, right_corners, right_found)
            # cv2.namedWindow('Left Image', cv2.WINDOW_NORMAL)
            # cv2.resizeWindow('Left Image', 700, 400)
            # cv2.imshow('Left Image', img_left)
            # cv2.waitKey(500)
            x = int(math.floor(index / self.matrix_width))
            y = int(index - (self.matrix_width * x))

            self.images_with_corners_left[720 * x: 720 * (x + 1), 1280 * y:1280 * (y + 1), :] = img_left
            self.images_with_corners_right[720 * x: 720 * (x + 1), 1280 * y:1280 * (y + 1), :] = img_right

    def calculate_euler_angles_from_rotation_matrix(self, rotation_matrix):
        sy = math.sqrt(rotation_matrix[0, 0] * rotation_matrix[0, 0] + rotation_matrix[1, 0] * rotation_matrix[1, 0])

        singular = sy < 1e-6

        if not singular:
            euler_x = math.atan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            euler_y = math.atan2(-rotation_matrix[2, 0], sy)
            euler_z = math.atan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            euler_x = math.atan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            euler_y = math.atan2(-rotation_matrix[2, 0], sy)
            euler_z = 0

        return euler_x, euler_y, euler_z

    def calculateCameraPointsFromMatrix(self, cameraMatrix1, depth=10):
        top_left = [((0 - cameraMatrix1[0, 2]) * depth) / cameraMatrix1[0, 0], ((0 - cameraMatrix1[1, 2]) * 10) / cameraMatrix1[1, 1], depth]
        top_right = [((1280 - cameraMatrix1[0, 2]) * depth) / cameraMatrix1[0, 0], ((720 - cameraMatrix1[1, 2]) * 10) / cameraMatrix1[1, 1], depth]
        bottom_right = [((1280 - cameraMatrix1[0, 2]) * depth) / cameraMatrix1[0, 0], ((0 - cameraMatrix1[1, 2]) * 10) / cameraMatrix1[1, 1], depth]
        bottom_left = [((0 - cameraMatrix1[0, 2]) * depth) / cameraMatrix1[0, 0], ((720 - cameraMatrix1[1, 2]) * 10) / cameraMatrix1[1, 1], depth]

        return top_left, top_right, bottom_left, bottom_right
