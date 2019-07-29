import cv2
import math
import numpy as np


class Transform3DPointsToDepthImageService:
    def __init__(self):
        pass

    def execute(self, points_3d, points_a_2d, image):
        image_points = np.zeros(image.shape)
        for point_3d, point_2d in zip(points_3d, points_a_2d):
            depth = math.sqrt((point_3d.x**2 + point_3d.y**2 + point_3d.z**2))
            #cv2.circle(image, (int(point_2d[0][0]), int(point_2d[0][1])), 3, (0, 0, depth), 2)
            font = cv2.FONT_HERSHEY_COMPLEX_SMALL
            cv2.putText(image, str(depth), (int(point_2d[0][0]), int(point_2d[0][1])), font, 1, (0, 0, 255), 2, cv2.LINE_AA)
            image_points[int(point_2d[0][1])][int(point_2d[0][0])] = (0, 0, depth)

        image_points[np.nonzero(image_points)] = abs((image_points[np.nonzero(image_points)] / np.amax(image_points)) - 1)
        self.showImage(image, 'circles')
        self.showImage(image_points, 'points')

    def showImage(self, image, name='image'):
        cv2.imshow(name, image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
