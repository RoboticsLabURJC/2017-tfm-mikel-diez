import numpy as np
import math


class CalculateDistanceBetweenTwoPixelProjectionsService:
    def __init__(self, stereo_calibration_data):
        self.stereo_calibration_data = stereo_calibration_data

    def execute(self, point_a, point_b):
        right_3d_point = self.backproject(
            point_b,
            self.stereo_calibration_data['cameraMatrix2'],
            self.stereo_calibration_data['R'],
            self.stereo_calibration_data['T']
        )

        left_3d_point = self.backproject(
            point_a,
            self.stereo_calibration_data['cameraMatrix1'],
            np.identity(3),
            np.array([[.0], [.0], [.0]])
        )

        right_3d_point = right_3d_point[:3]
        left_3d_point = left_3d_point[:3]

        left_3d_point = left_3d_point * -10000

        center_a = np.array([.0, .0, .0])

        center_b = self.rotate_point(center_a, self.stereo_calibration_data['R'])
        center_b = self.translate_point(center_b, self.stereo_calibration_data['T'].reshape(3))

        right_3d_point[0] = center_b[0] + (right_3d_point[0] - center_b[0]) * -10000
        right_3d_point[1] = center_b[1] + (right_3d_point[1] - center_b[1]) * -10000
        right_3d_point[2] = center_b[2] + (right_3d_point[2] - center_b[2]) * -10000

        distance = self.calculate_distance_between_lines(center_a, left_3d_point, center_b, right_3d_point)
        return distance

    def backproject(self, point2d, K, R, T):
        RT = np.hstack((R, T))
        RT = np.vstack((RT, [0, 0, 0, 1]))
        iK = np.linalg.inv(K)
        Pi = np.array([point2d[0], point2d[1], 1.0], dtype=np.double).reshape(3, 1)
        a = np.dot(iK, Pi)
        aH = np.array([a[0], a[1], a[2], 1], dtype=np.double)
        RT2 = RT.copy()
        RT2[0, 3] = 0
        RT2[1, 3] = 0
        RT2[2, 3] = 0
        RT2[3, 3] = 1
        b = np.dot(np.transpose(RT2), aH)
        translate = np.identity(4, dtype=np.double)
        translate[0, 3] = RT[0, 3] / RT[3, 3]
        translate[1, 3] = RT[1, 3] / RT[3, 3]
        translate[2, 3] = RT[2, 3] / RT[3, 3]
        b = np.dot(translate, b)
        outPoint = np.array([b[0] / b[3], b[1] / b[3], b[2] / b[3], 1])
        return outPoint

    def calculate_distance_between_lines(self, p1_a, p2_a, p1_b, p2_b):
        SMALL_NUM = 0.00000001

        u = p1_a - p2_a
        v = p1_b - p2_b
        w = p1_a - p1_b

        a = (u[0] * u[0] + u[1] * u[1] + u[2] * u[2])
        b = (u[0] * v[0] + u[1] * v[1] + u[2] * v[2])
        c = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
        d = (u[0] * w[0] + u[1] * w[1] + u[2] * w[2])
        e = (v[0] * w[0] + v[1] * w[1] + v[2] * w[2])
        D = (a * c) - (b * b)

        sc = 0.0
        tc = 0.0

        if D < SMALL_NUM:
            sc = 0.0
            tc = d/b if b>c else e/c
        else:
            sc = (b*e - c*d) / D
            tc = (a*e - b*d) / D

        dP = w + (sc * u) - (tc * v)

        return math.sqrt((dP[0] * dP[0] + dP[1] * dP[1] + dP[2] * dP[2]))

    def rotate_point(self, point, rotation_matrix):
        return np.dot(rotation_matrix, point.T)

    def translate_point(self, point, translation_vector):
        return point + translation_vector