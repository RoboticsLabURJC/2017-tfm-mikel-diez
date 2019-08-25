import cv2
import math
import numpy as np


class Transform3DPointsToDepthImageService:
    def execute(self, points_3d, points_a_2d, image):
        image_points = np.zeros(image.shape[0:2])
        for point_3d, point_2d in zip(points_3d, points_a_2d):
            depth = math.sqrt((point_3d.x**2 + point_3d.y**2 + point_3d.z**2))
            image_points[int(point_2d[0][1])][int(point_2d[0][0])] = self.scale_depth(depth)

        self.show_image(image_points / image_points.max(), 'points')

    @staticmethod
    def draw_circle_in_image(depth, image, point_2d):
        cv2.circle(image, (int(point_2d[0][0]), int(point_2d[0][1])), 3, (0, 0, depth * 255), 2)

    @staticmethod
    def print_depth_to_image(depth, image, point_2d):
        font = cv2.FONT_HERSHEY_COMPLEX_SMALL
        cv2.putText(image, str(depth), (int(point_2d[0][0]), int(point_2d[0][1])), font, 1, (0, 0, 255), 2, cv2.LINE_AA)

    @staticmethod
    def show_image(image, name='image'):
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    @staticmethod
    def scale_depth(depth):
        if depth < 50:
            return 0
        else:
            return 1/depth

