from Vision.Repositories.depthImagePointsRepository import depthImagePointsRepository


class Transform3DPointsToDepthFileService:
    def __init__(self):
        self.depthImageRepository = depthImagePointsRepository()

    def execute(self, points_3d, points_a_2d, calibration_data):
        self.depthImageRepository.saveInPath(
            'bin/second_test.txt',
            points_3d,
            points_a_2d
        )

        self.depthImageRepository.readFromPath('bin/second_test.txt')
