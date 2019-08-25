import numpy as np
import jderobot


class Reconstruct3DPointsUsingGeometryService:
    REAL_WORLD_TRANSFORMATION = np.array([
            np.array([1., .0, .0]),
            np.array([.0, .0, -1.]),
            np.array([.0, 1., 0.])
        ])

    def __init__(self, stereo_calibration, image_a, image_b):
        self.stereo_calibration = stereo_calibration
        self.image_a = image_a
        self.image_b = image_b

    def execute(self, points_a, points_b):
        pass

    def __transform_points_to_world_coordinates(self, points4d, a_points):
        final_points = []

        for index in range(0, a_points.shape[0] - 0):
            transformed_point = np.array([float(points4d[0][index] / points4d[3][index]), float(points4d[1][index] / points4d[3][index]), float(points4d[2][index] / points4d[3][index])])
            transformed_point = self.REAL_WORLD_TRANSFORMATION.dot(transformed_point) / 10.0
            red = float(self.image_a[int(a_points[index][0][1])][int(a_points[index][0][0])][2]/255.0)
            green = float(self.image_a[int(a_points[index][0][1])][int(a_points[index][0][0])][1]/255.0)
            blue = float(self.image_a[int(a_points[index][0][1])][int(a_points[index][0][0])][0]/255.0)
            final_points.append(jderobot.RGBPoint(transformed_point[0], transformed_point[1], transformed_point[2], red, green, blue))

        return final_points
