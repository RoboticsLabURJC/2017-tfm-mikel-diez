from src.vision.shared.presentation.repositories.depthImagePointsRepository import depthImagePointsRepository


class Transform3DPointsToDepthFileService:
    def __init__(self):
        self.depthImageRepository = depthImagePointsRepository()

    def execute(self, points_3d, points_a_2d, calibration_data, image):
        self.depthImageRepository.saveInPathWithImage(
            'bin/second_test.txt',
            points_3d,
            points_a_2d,
            (image.shape[0], image.shape[1])
        )

        self.depthImageRepository.readFromPath('bin/second_test.txt')
