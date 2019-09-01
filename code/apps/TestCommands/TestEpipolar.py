import yaml
import numpy as np
import jderobot
from src.vision.presentation.services.GetCameraRepresentationWithRotationAndTranslationService import GetCameraRepresentationWithRotationAndTranslationService
from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer

REAL_WORLD_TRANSFORMATION = np.array([
        np.array([1., .0, .0]),
        np.array([.0, .0, -1.]),
        np.array([.0, 1., 0.])
    ])

def rotate_points(point, rotation_matrix):
    return np.dot(rotation_matrix, point.T)


def translate_points(point, translation_vector):
    return point - translation_vector

def transform_points_to_real_world(point):
       return REAL_WORLD_TRANSFORMATION.dot(point)

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

            point_a = [845, 149]
            point_b = [809, 284]

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

            camera_matrix = stereoCalibrationData['cameraMatrix1']
            left_3d_point = np.array([((point_a[0] - camera_matrix[0, 2]) * -2) / camera_matrix[0, 0],
                                 ((point_a[1] - camera_matrix[1, 2]) * -2) / camera_matrix[1, 1], -2])

            camera_matrix = stereoCalibrationData['cameraMatrix2']
            right_3d_point = np.array([((point_b[0] - camera_matrix[0, 2]) * -2) / camera_matrix[0, 0],
                                 ((point_b[1] - camera_matrix[1, 2]) * -2) / camera_matrix[1, 1], -2])

            left_3d_point = left_3d_point / (np.linalg.norm(left_3d_point) / 2)
            right_3d_point = right_3d_point / (np.linalg.norm(right_3d_point) / 2)

            right_3d_point = rotate_points(right_3d_point, stereoCalibrationData['R'])

            right_3d_point = translate_points(right_3d_point, stereoCalibrationData['T'].reshape(3) / 10)

            left_3d_point = transform_points_to_real_world(left_3d_point)
            right_3d_point = transform_points_to_real_world(right_3d_point)

            left_3d_point = left_3d_point * 100

            center_a = np.array([.0, .0, .0])

            camera_color = jderobot.Color(0.0, 0.0, 1.0)
            segments += [jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0, 0, 0),
                             jderobot.Point(left_3d_point[0], left_3d_point[1], left_3d_point[2])),
            camera_color)]

            center_b = translate_points(center_a, stereoCalibrationData['T'].reshape(3) / 10)
            center_b = transform_points_to_real_world(center_b)

            right_3d_point[0] = center_b[0] + (right_3d_point[0] - center_b[0]) * 100
            right_3d_point[1] = center_b[1] + (right_3d_point[1] - center_b[1]) * 100
            right_3d_point[2] = center_b[2] + (right_3d_point[2] - center_b[2]) * 100

            segments += [jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(center_b[0], center_b[1], center_b[2]),
                                 jderobot.Point(right_3d_point[0], right_3d_point[1], right_3d_point[2])),
                camera_color)]



            vision_viewer = VisionViewer()
            vision_viewer.set_points(points)
            vision_viewer.set_segments(segments)
            vision_server = VisualServer(vision_viewer)
            vision_server.run()


        except yaml.YAMLError as exc:
            print(exc)





