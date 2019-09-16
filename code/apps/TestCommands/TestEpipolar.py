import jderobot
import numpy as np
import yaml
from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer
from src.vision.presentation.services.GetCameraRepresentationWithRotationAndTranslationService import \
    GetCameraRepresentationWithRotationAndTranslationService

from src.vision.matching.services.CalculateDistanceBetweenTwoPixelProjectionsService import CalculateDistanceBetweenTwoPixelProjectionsService

import math

REAL_WORLD_TRANSFORMATION = np.array([
        np.array([1., .0, .0]),
        np.array([.0, .0, -1.]),
        np.array([.0, 1., 0.])
    ])


def backproject2(point2d, K, R, T):
    RT = np.hstack((R, T))
    RT = np.vstack((RT, [0, 0, 0, 1]))
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

def shortest_distance_between_lines(p1_a, p2_a, p1_b, p2_b):
    SMALL_NUM = 0.00000001

    u = p1_a - p2_a
    v = p1_b - p2_b
    w = p1_a - p1_b

    a = (u[0] * u[0] + u[1] * u[1] + u[2] * u[2])
    b = (u[0] * v[0] + u[1] * v[1] + u[2] * v[2])
    c = (v[0] * v[0] + v[1] * v[1] + v[2] * v[2])
    d = (u[0] * w[0] + u[1] * w[1] + u[2] * w[2])
    e = (v[0] * w[0] + v[1] * w[1] + v[2] * w[2])
    D = (a * c) - (b * b)

    sc = 0.0
    tc = 0.0

    if D < SMALL_NUM:
        sc = 0.0
        tc = d/b if b>c else e/c
    else:
        sc = (b*e - c*d) / D
        tc = (a*e - b*d) / D

    dP = w + (sc * u) - (tc * v)

    return math.sqrt((dP[0] * dP[0] + dP[1] * dP[1] + dP[2] * dP[2]))


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

            calculateDistanceBetweenTwoPixelProjectionsService = CalculateDistanceBetweenTwoPixelProjectionsService(stereoCalibrationData)

            print('k1', stereoCalibrationData['cameraMatrix1'])
            print('k2', stereoCalibrationData['cameraMatrix2'])
            print('R', stereoCalibrationData['R'])
            print('T', stereoCalibrationData['T'])

            point_a = [325, 154]
            point_b = [1000, 700]

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

            right_3d_point = backproject2(
                point_b,
                stereoCalibrationData['cameraMatrix2'],
                stereoCalibrationData['R'],
                stereoCalibrationData['T']
            )

            left_3d_point = backproject2(
                point_a,
                stereoCalibrationData['cameraMatrix1'],
                np.identity(3),
                np.array([[.0], [.0], [.0]])
            )

            right_3d_point = right_3d_point[:3] / 10
            left_3d_point = left_3d_point[:3] / 10

            left_3d_point = transform_points_to_real_world(left_3d_point)
            right_3d_point = transform_points_to_real_world(right_3d_point)

            left_3d_point = left_3d_point * -10000

            center_a = np.array([.0, .0, .0])

            camera_color = jderobot.Color(0.0, 0.0, 1.0)
            segments += [jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0, 0, 0),
                             jderobot.Point(left_3d_point[0], left_3d_point[1], left_3d_point[2])),
            camera_color)]

            center_b = rotate_points(center_a, stereoCalibrationData['R'])
            center_b = translate_points(center_b, stereoCalibrationData['T'].reshape(3) / 10)
            center_b = transform_points_to_real_world(center_b)

            print('center', center_b)

            right_3d_point[0] = center_b[0] + (right_3d_point[0] - center_b[0]) * -10000
            right_3d_point[1] = center_b[1] + (right_3d_point[1] - center_b[1]) * -10000
            right_3d_point[2] = center_b[2] + (right_3d_point[2] - center_b[2]) * -10000



            segments += [jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(center_b[0], center_b[1], center_b[2]),
                                 jderobot.Point(right_3d_point[0], right_3d_point[1], right_3d_point[2])),
                camera_color)]

            distance = shortest_distance_between_lines(center_a, left_3d_point, center_b, right_3d_point)
            print('distance: ', distance)

            calculateDistanceBetweenTwoPixelProjectionsService.execute(point_a, point_b)

            vision_viewer = VisionViewer()
            vision_viewer.set_points(points)
            vision_viewer.set_segments(segments)
            vision_server = VisualServer(vision_viewer)
            vision_server.run()


        except yaml.YAMLError as exc:
            print(exc)





