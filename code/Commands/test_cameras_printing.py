import yaml
import numpy as np
from Vision.Services.GetCameraRepresentationWithRotationAndTranslationService import GetCameraRepresentationWithRotationAndTranslationService
from Vision.Components.Visualization.visualization import VisionViewer
from Vision.Components.Visualization.visualization_server import VisualServer


if __name__ == '__main__':
    images_set = 'set_canonical'
    stereoCalibration = 'bin/sets/' + images_set + '/calibrated_camera.yml'
    cameraACalibration = 'bin/sets/' + images_set + '/camera_A_calibration.yml'
    cameraBCalibration = 'bin/sets/' + images_set + '/camera_B_calibration.yml'
    with open(stereoCalibration, 'r') as stereoCalibration, open(cameraACalibration, 'r') as cameraACalibration, open(cameraBCalibration, 'r') as cameraBCalibration:
        try:
            stereoCalibrationData = yaml.load(stereoCalibration, Loader=yaml.UnsafeLoader)
            cameraACalibrationData = yaml.load(cameraACalibration, Loader=yaml.UnsafeLoader)
            cameraBCalibrationData = yaml.load(cameraBCalibration, Loader=yaml.UnsafeLoader)

            segments = []
            points = []

            camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
            segments += camera_generator.execute(
                np.array(stereoCalibrationData['cameraMatrix2']),
                np.array(stereoCalibrationData['distCoeffs2']),
                np.array(stereoCalibrationData['r2']),
                np.array(stereoCalibrationData['p2']),
                np.array(stereoCalibrationData['R']),
                np.array(stereoCalibrationData['T'])
            )
            camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
            segments += camera_generator.execute(
                np.array(stereoCalibrationData['cameraMatrix1']),
                np.array(stereoCalibrationData['distCoeffs1']),
                np.array(stereoCalibrationData['r1']),
                np.array(stereoCalibrationData['p1']),
                np.identity(3),
                np.array([.0, .0, .0])
            )

            vision_viewer = VisionViewer()
            vision_viewer.set_points(points)
            vision_viewer.set_segments(segments)
            vision_server = VisualServer(vision_viewer)
            vision_server.run()


        except yaml.YAMLError as exc:
            print(exc)





