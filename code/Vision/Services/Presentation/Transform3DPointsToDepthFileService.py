import math


class Transform3DPointsToDepthFileService:

    RELEVANT_CALIBRATION_PARAMETERS = ['cameraMatrix1', 'distCoeffs1', 'p1']

    def __init__(self):
        pass

    def execute(self, points_3d, points_a_2d, calibration_data):
        file = open('bin/test_file.txt', 'w+')

        self.printPointsToFile(file, points_3d, points_a_2d)
        self.printCalibrationToFile(file, calibration_data)

        file.close()

    def printPointsToFile(self, file, points_3d, points_a_2d):
        file.write('# points (x, y, depth)\n')
        for point_3d, point_2d in zip(points_3d, points_a_2d):
            depth = math.sqrt((point_3d.x ** 2 + point_3d.y ** 2 + point_3d.z ** 2))
            file.write(str(point_2d[0][0]) + ' ' + str(point_2d[0][1]) + ' ' + str(depth) + '\n')

    def printCalibrationToFile(self, file, calibration_data):
        file.write('calibration_data\n')
        for value in calibration_data:
            if value in self.RELEVANT_CALIBRATION_PARAMETERS:
                file.write(value + '\n')
                print(','.join(','.join(str(column) for column in row) for row in calibration_data[value]))
                file.write(','.join(','.join(str(column) for column in row) for row in calibration_data[value]) + '\n')
                print(str(calibration_data[value]))
