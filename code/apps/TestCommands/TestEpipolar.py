import jderobot
import numpy as np
import yaml
from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer
from src.vision.presentation.services.GetCameraRepresentationWithRotationAndTranslationService import \
    GetCameraRepresentationWithRotationAndTranslationService

REAL_WORLD_TRANSFORMATION = np.array([
        np.array([1., .0, .0]),
        np.array([.0, .0, -1.]),
        np.array([.0, 1., 0.])
    ])


def backproject2(point2d, K, R, T):
    print(R)
    print(T)
    RT = np.hstack((R, T))
    RT = np.vstack((RT, [0, 0, 0, 1]))
    print(RT)
    iK = np.linalg.inv(K)
    Pi = np.array([point2d[0], point2d[1], 1.0], dtype=np.double).reshape(3, 1)
    a = np.dot(iK, Pi)
    aH = np.array([a[0], a[1], a[2], 1], dtype=np.double)
    RT2 = RT.copy()
    RT2[0, 3] = 0
    RT2[1, 3] = 0
    RT2[2, 3] = 0
    RT2[3, 3] = 1
    b = np.dot(np.transpose(RT2), aH)
    translate = np.identity(4, dtype=np.double)
    translate[0, 3] = RT[0, 3] / RT[3, 3]
    translate[1, 3] = RT[1, 3] / RT[3, 3]
    translate[2, 3] = RT[2, 3] / RT[3, 3]
    b = np.dot(translate, b)
    outPoint = np.array([b[0] / b[3], b[1] / b[3], b[2] / b[3], 1])
    return outPoint

def rotate_points(point, rotation_matrix):
    return np.dot(rotation_matrix, point.T)


def translate_points(point, translation_vector):
    return point + translation_vector

def transform_points_to_real_world(point):
       return REAL_WORLD_TRANSFORMATION.dot(point)

if __name__ == '__main__':
    images_set = 'set_canonical'
    stereoCalibration = 'bin/sets/' + images_set + '/calibrated_camera.yml'
    with open(stereoCalibration, 'r') as stereoCalibration:
        try:
            stereoCalibrationData = yaml.load(stereoCalibration, Loader=yaml.UnsafeLoader)

            print(stereoCalibrationData['cameraMatrix1'])
            print(stereoCalibrationData['cameraMatrix2'])

            point_a = [872, 72]
            point_b = [833, 206]

            segments = []
            points = []
            camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
            segments += camera_generator.execute(
                np.array(stereoCalibrationData['cameraMatrix2']),
                np.array(stereoCalibrationData['distCoeffs2']),
                None,
                None,
                np.array(stereoCalibrationData['R']),
                np.array(stereoCalibrationData['T'])
            )
            camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
            segments += camera_generator.execute(
                np.array(stereoCalibrationData['cameraMatrix1']),
                np.array(stereoCalibrationData['distCoeffs1']),
                None,
                None,
                np.identity(3),
                np.array([.0, .0, .0])
            )

            camera_matrix = stereoCalibrationData['cameraMatrix1']
            left_3d_point = np.array(
                [
                    ((point_a[0] - camera_matrix[0, 2]) * -2) / camera_matrix[0, 0],
                    ((point_a[1] - camera_matrix[1, 2]) * -2) / camera_matrix[1, 1],
                    -2
                ]
            )

            camera_matrix = stereoCalibrationData['cameraMatrix2']
            right_3d_point = np.array(
                [
                    ((point_b[0] - camera_matrix[0, 2]) * -2) / camera_matrix[0, 0],
                    ((point_b[1] - camera_matrix[1, 2]) * -2) / camera_matrix[1, 1],
                    -2
                ]
            )

            #left_3d_point = left_3d_point / (np.linalg.norm(left_3d_point) / 2)
            #right_3d_point = right_3d_point / (np.linalg.norm(right_3d_point) / 2)

            right_3d_point = translate_points(right_3d_point, stereoCalibrationData['T'].reshape(3) / 10)

            right_3d_point = rotate_points(right_3d_point, stereoCalibrationData['R'])

            right_3d_point = backproject2(
                point_b,
                stereoCalibrationData['cameraMatrix2'],
                stereoCalibrationData['R'],
                stereoCalibrationData['T']
            )

            left_3d_point = backproject2(
                point_b,
                stereoCalibrationData['cameraMatrix1'],
                np.identity(3),
                np.array([[.0], [.0], [.0]])
            )


            right_3d_point = right_3d_point[:3] / 10
            left_3d_point = left_3d_point[:3] / 10

            left_3d_point = transform_points_to_real_world(left_3d_point)
            right_3d_point = transform_points_to_real_world(right_3d_point)

            left_3d_point = left_3d_point * -1000

            center_a = np.array([.0, .0, .0])

            camera_color = jderobot.Color(0.0, 0.0, 1.0)
            segments += [jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0, 0, 0),
                             jderobot.Point(left_3d_point[0], left_3d_point[1], left_3d_point[2])),
            camera_color)]

            center_b = translate_points(center_a, stereoCalibrationData['T'].reshape(3) / 10)
            #center_b = rotate_points(center_b, stereoCalibrationData['R'])
            center_b = transform_points_to_real_world(center_b)

            print(center_b)

            right_3d_point[0] = center_b[0] + (right_3d_point[0] - center_b[0]) * -10000
            right_3d_point[1] = center_b[1] + (right_3d_point[1] - center_b[1]) * -10000
            right_3d_point[2] = center_b[2] + (right_3d_point[2] - center_b[2]) * -10000



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





