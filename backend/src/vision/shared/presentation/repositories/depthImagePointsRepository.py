import math
import numpy as np


class depthImagePointsRepository:
    def readFromPath(self, path):
        file = open(path, 'r')
        image_points = []
        for line in file:
            if '#' is line[:1]:
                print(line)
            else:
                image_points.append(np.array(line.split()))

        return np.array(image_points)

    def saveInPath(self, path, points_3d, points_2d):
        file = open(path, 'w+')

        file.write('# points (x, y, depth)\n')
        for point_3d, point_2d in zip(points_3d, points_2d):
            depth = math.sqrt((point_3d.x ** 2 + point_3d.y ** 2 + point_3d.z ** 2))
            file.write(str(point_2d[0][0]) + ' ' + str(point_2d[0][1]) + ' ' + str(depth) + '\n')

        file.close()

    def saveInPathWithImage(self, path, points_3d, points_2d, size):
        file = open(path, 'w+')
        image = np.zeros(size)
        file.write('# points (x, y, depth)\n')
        for point_3d, point_2d in zip(points_3d, points_2d):
            depth = math.sqrt((point_3d.x ** 2 + point_3d.y ** 2 + point_3d.z ** 2))
            image[int(point_2d[0][1])][int(point_2d[0][0])] = depth

        for column in range(size[0]):
            for row in range(size[1]):
                file.write(str(row) + ' ' + str(column) + ' ' + str(image[column][row]) + '\n')

        file.close()