import logging
from datetime import datetime

import cv2
import jderobot
import numpy as np
import yaml
from Vision.Components.Reconstruction.Reconstructor3D import Reconstructor3D
from Vision.Components.Visualization.visualization import VisionViewer
from Vision.Components.Visualization.visualization_server import VisualServer
from Vision.Services.GetCameraRepresentationWithRotationAndTranslationService import \
    GetCameraRepresentationWithRotationAndTranslationService
from Vision.Services.Matching.MatchInterestPointsWithBrisk import MatchInterestPointsWithBrisk as GetMatchedPointsService


class ReconstructionFromImages:
    def __init__(self, image01, image02, stereoCalibration, cameraACalibration, cameraBCalibration, gui):
        self.gui = gui
        self.image01 = image01
        self.image02 = image02
        self.calibration = stereoCalibration
        self.cameraACalibration = cameraACalibration
        self.cameraBCalibration = cameraBCalibration
        self.segments = []
        self.points = []
        self.distance = 900
        self.camera_distance = 90
        logging.getLogger().setLevel(logging.INFO)

    def run(self):
        with open(self.calibration, 'r') as stereoCalibration, open(self.cameraACalibration, 'r') as cameraACalibration, open(self.cameraBCalibration, 'r') as cameraBCalibration:
            try:
                initial_time = datetime.now()
                logging.info('[{}] Load Images'.format(datetime.now().time()))
                image1 = cv2.imread(self.image01)
                image2 = cv2.imread(self.image02)
                stereoCalibrationData = yaml.load(stereoCalibration, Loader=yaml.UnsafeLoader)
                cameraACalibrationData = yaml.load(cameraACalibration, Loader=yaml.UnsafeLoader)
                cameraBCalibrationData = yaml.load(cameraBCalibration, Loader=yaml.UnsafeLoader)

                get_matched_interest_points_from_images_service = GetMatchedPointsService(
                    stereoCalibrationData
                )

                logging.info('[{}] Start Match Points'.format(datetime.now().time()))
                left_points, right_points = get_matched_interest_points_from_images_service.execute(image1, image2)
                reconstructor = Reconstructor3D(stereoCalibrationData, image1, image2)



                self.points = reconstructor.execute(left_points, right_points)

                logging.info('[{}] End Match Points'.format(datetime.now().time()))

                logging.info('[{}] Setting Points and Segments'.format(datetime.now().time()))
                # self.print_cameras()
                camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
                self.segments += camera_generator.execute(
                    np.array(stereoCalibrationData['cameraMatrix2']),
                    np.array(stereoCalibrationData['distCoeffs2']),
                    np.array(stereoCalibrationData['r2']),
                    np.array(stereoCalibrationData['p2']),
                    np.array(stereoCalibrationData['R']),
                    np.array(stereoCalibrationData['T'])
                )
                camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
                self.segments += camera_generator.execute(
                    np.array(stereoCalibrationData['cameraMatrix1']),
                    np.array(stereoCalibrationData['distCoeffs1']),
                    np.array(stereoCalibrationData['r1']),
                    np.array(stereoCalibrationData['p1']),
                    np.identity(3),
                    np.array([.0, .0, .0])
                )
                self.print_coordinates_reference()
                self.print_reference_plane()

                vision_viewer = VisionViewer()
                vision_viewer.set_points(self.points)
                vision_viewer.set_segments(self.segments)
                vision_server = VisualServer(vision_viewer)
                logging.info('[{}] Run vision server'.format(datetime.now().time()))
                vision_server.run()

                end_time = datetime.now()
                logging.info('Total time: {}'.format(end_time - initial_time))

            except yaml.YAMLError as exc:
                print(exc)

    def print_coordinates_reference(self):
        self.segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(10.0, 0.0, 0.0), jderobot.Point(0.0, 0.0, 0.0)),
                jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(0.0, 10.0, 0.0), jderobot.Point(0.0, 0.0, 0.0)),
                jderobot.Color(0.0, 1.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(0.0, 0.0, 10.0), jderobot.Point(0.0, 0.0, 0.0)),
                jderobot.Color(0.0, 0.0, 1.0)))

    def print_reference_plane(self):
        distance = (self.distance * 3.4 / self.camera_distance)
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, distance, 50.0), jderobot.Point(50.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, distance, -50.0), jderobot.Point(-50.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -50.0), jderobot.Point(-50.0, distance, 50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 50.0), jderobot.Point(50.0, distance, 50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 40.0), jderobot.Point(50.0, distance, 40.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 30.0), jderobot.Point(50.0, distance, 30.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 20.0), jderobot.Point(50.0, distance, 20.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 10.0), jderobot.Point(50.0, distance, 10.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 0.0), jderobot.Point(50.0,  distance, 0.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -10.0), jderobot.Point(50.0, distance, -10.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -20.0), jderobot.Point(50.0, distance, -20.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -30.0), jderobot.Point(50.0, distance, -30.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -40.0), jderobot.Point(50.0, distance, -40.0)),
            jderobot.Color(1.0, 0.0, 0.0)))

        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(40.0, distance, 50.0), jderobot.Point(40.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(30.0, distance, 50.0), jderobot.Point(30.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(20.0, distance, 50.0), jderobot.Point(20.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(10.0, distance, 50.0), jderobot.Point(10.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, distance, 50.0), jderobot.Point(0.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-10.0, distance, 50.0), jderobot.Point(-10.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-20.0, distance, 50.0), jderobot.Point(-20.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-30.0, distance, 50.0), jderobot.Point(-30.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-40.0, distance, 50.0), jderobot.Point(-40.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))

    def print_cameras(self):
        self.points.append(jderobot.RGBPoint(-3.44965908, 1.22125194e-17, 0.0, 0.0, 0.0, 0.0))
        self.points.append(jderobot.RGBPoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908, 1.22125194e-17, 0.0),
                             jderobot.Point(-3.44965908 - 0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908, 1.22125194e-17, 0.0),
                             jderobot.Point(-3.44965908 + 0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908, 1.22125194e-17, 0.0),
                             jderobot.Point(-3.44965908 - 0.75, 1.5, -0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908, 1.22125194e-17, 0.0),
                             jderobot.Point(-3.44965908 + 0.75, 1.5, -0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908 - 0.75, 1.5, - 0.75),
                             jderobot.Point(-3.44965908 - 0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908 + 0.75, 1.5, - 0.75),
                             jderobot.Point(-3.44965908 + 0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908 + 0.75, 1.5, - 0.75),
                             jderobot.Point(-3.44965908 - 0.75, 1.5, - 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-3.44965908 + 0.75, 1.5,  0.75),
                             jderobot.Point(-3.44965908 - 0.75, 1.5,  0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))

        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, 1.22125194e-17, 0.0),
                             jderobot.Point(- 0.75, 1.5, 0.75)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, 1.22125194e-17, 0.0),
                             jderobot.Point(0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 1.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, 1.22125194e-17, 0.0),
                             jderobot.Point(- 0.75, 1.5, -0.75)),
            jderobot.Color(0.0, 0.0, 1.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, 1.22125194e-17, 0.0),
                             jderobot.Point(0.75, 1.5, -0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(- 0.75, 1.5, - 0.75),
                             jderobot.Point(- 0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.75, 1.5, - 0.75),
                             jderobot.Point(0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.75, 1.5, - 0.75),
                             jderobot.Point(- 0.75, 1.5, - 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.75, 1.5, 0.75),
                             jderobot.Point(- 0.75, 1.5, 0.75)),
            jderobot.Color(0.0, 0.0, 0.0)))