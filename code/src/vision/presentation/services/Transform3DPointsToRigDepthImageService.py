import cv2
import math
import numpy as np


class Transform3DPointsToRigDepthImageService:
    def __init__(self):
        pass

    def execute(self, points_3d, calibration_data):
        points_3d = self.transform_3d_points(points_3d)
        points_2d, _ = cv2.projectPoints(
            points_3d,
            calibration_data['R'],
            calibration_data['T'],
            calibration_data['cameraMatrix1'],
            calibration_data['distCoeffs1']
        )
        depths = []

        for point_3d in points_3d:
            depth = math.sqrt((point_3d[0]**2 + point_3d[0]**2 + point_3d[0]**2))
            depths.append(depth)

        self.show_image(points_2d)

    @staticmethod
    def show_image(points, name='image'):
        image = np.zeros((1280, 720))
        print(points.shape)
        for point in points:
            print(point.shape)
            image[int(point[0][0])][int(point[0][1])] = 255
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def transform_3d_points(self, points_3d):
        points_3d_transformed = []
        for point_3d in points_3d:
            points_3d_transformed.append(np.array([point_3d.x, point_3d.y, point_3d.z]))

        return np.array(points_3d_transformed)