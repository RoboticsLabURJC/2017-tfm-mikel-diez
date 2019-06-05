import jderobot
import numpy as np
import cv2

class GetCameraRepresentationWithRotationAndTranslationService:
    REAL_WORLD_TRANSFORMATION = np.array([
        np.array([1., .0, .0]),
        np.array([.0, .0, -1.]),
        np.array([.0, 1., 0.])
    ])

    def __init__(self):
        self.camera_center = np.array([.0, .0, .0])
        self.top_left_corner = None
        self.top_right_corner = None
        self.bottom_left_corner = None
        self.bottom_right_corner = None
        self.camera_color = jderobot.Color(0.0, 0.0, 0.0)
        self.segments = []

    def execute(self, camera_matrix, dist_coeffs, r, p, rotation_matrix, translation_vector, scale=10):
        self.top_left_corner, self.top_right_corner, self.bottom_left_corner, self.bottom_right_corner = self.calculate_camera_points_from_matrix(camera_matrix, dist_coeffs, r, p)

        self.rotate_points(rotation_matrix)
        self.translate_points(translation_vector.reshape(3) / scale)
        self.transform_points_to_real_world()

        self.generate_camera_segments()

        return self.segments

    def rotate_points(self, rotation_matrix):
        self.top_left_corner = np.dot(rotation_matrix, self.top_left_corner.T)
        self.top_right_corner = np.dot(rotation_matrix, self.top_right_corner.T)
        self.bottom_left_corner = np.dot(rotation_matrix, self.bottom_left_corner.T)
        self.bottom_right_corner = np.dot(rotation_matrix, self.bottom_right_corner.T)

    def translate_points(self, translation_vector):
        self.camera_center -= translation_vector
        self.top_left_corner -= translation_vector
        self.top_right_corner -= translation_vector
        self.bottom_left_corner -= translation_vector
        self.bottom_right_corner -= translation_vector

    def generate_camera_segments(self):
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.camera_center[0], self.camera_center[1], self.camera_center[2]),
                             jderobot.Point(self.top_left_corner[0], self.top_left_corner[1], self.top_left_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.camera_center[0], self.camera_center[1], self.camera_center[2]),
                             jderobot.Point(self.top_right_corner[0], self.top_right_corner[1], self.top_right_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.camera_center[0], self.camera_center[1], self.camera_center[2]),
                             jderobot.Point(self.bottom_left_corner[0], self.bottom_left_corner[1], self.bottom_left_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.camera_center[0], self.camera_center[1], self.camera_center[2]),
                             jderobot.Point(self.bottom_right_corner[0], self.bottom_right_corner[1], self.bottom_right_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.top_left_corner[0], self.top_left_corner[1], self.top_left_corner[2]),
                             jderobot.Point(self.top_right_corner[0], self.top_right_corner[1], self.top_right_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.top_right_corner[0], self.top_right_corner[1], self.top_right_corner[2]),
                             jderobot.Point(self.bottom_right_corner[0], self.bottom_right_corner[1], self.bottom_right_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.bottom_right_corner[0], self.bottom_right_corner[1], self.bottom_right_corner[2]),
                             jderobot.Point(self.bottom_left_corner[0], self.bottom_left_corner[1], self.bottom_left_corner[2])),
            self.camera_color))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(self.bottom_left_corner[0], self.bottom_left_corner[1], self.bottom_left_corner[2]),
                             jderobot.Point(self.top_left_corner[0], self.top_left_corner[1], self.top_left_corner[2])),
            self.camera_color))

    def transform_points_to_real_world(self):
        self.camera_center = self.REAL_WORLD_TRANSFORMATION.dot(self.camera_center)
        self.top_left_corner = self.REAL_WORLD_TRANSFORMATION.dot(self.top_left_corner)
        self.top_right_corner = self.REAL_WORLD_TRANSFORMATION.dot(self.top_right_corner)
        self.bottom_left_corner = self.REAL_WORLD_TRANSFORMATION.dot(self.bottom_left_corner)
        self.bottom_right_corner = self.REAL_WORLD_TRANSFORMATION.dot(self.bottom_right_corner)

    @staticmethod
    def calculate_camera_points_from_matrix(camera_matrix, dist_coeffs, r, p, depth=-2):
        points_2d = np.array([
            [[0, 0]],
            [[0, 719]],
            [[1279, 0]],
            [[1279, 719]]
        ], dtype=np.float32)
        top_left = np.array([((points_2d[0][0][0] - camera_matrix[0, 2]) * depth) / camera_matrix[0, 0], ((points_2d[0][0][1] - camera_matrix[1, 2]) * depth) / camera_matrix[1, 1], depth])
        bottom_right = np.array([((points_2d[3][0][0] - camera_matrix[0, 2]) * depth) / camera_matrix[0, 0], ((points_2d[3][0][1] - camera_matrix[1, 2]) * depth) / camera_matrix[1, 1], depth])
        top_right = np.array([((points_2d[2][0][0] - camera_matrix[0, 2]) * depth) / camera_matrix[0, 0], ((points_2d[2][0][1] - camera_matrix[1, 2]) * depth) / camera_matrix[1, 1], depth])
        bottom_left = np.array([((points_2d[1][0][0] - camera_matrix[0, 2]) * depth) / camera_matrix[0, 0], ((points_2d[1][0][1] - camera_matrix[1, 2]) * depth) / camera_matrix[1, 1], depth])

        top_left = top_left / (np.linalg.norm(top_left) / 2)
        top_right = top_right / (np.linalg.norm(top_right) / 2)
        bottom_right = bottom_right / (np.linalg.norm(bottom_right) / 2)
        bottom_left = bottom_left / (np.linalg.norm(bottom_left) / 2)

        return top_left, top_right, bottom_left, bottom_right
