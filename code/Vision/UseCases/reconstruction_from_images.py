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
from Vision.Services.Matching.MatchInterestPointsWithBRIEF import MatchInterestPointsWithBRIEF as GetMatchedPointsService
from Vision.Services.Presentation.Transform3DPointsToDepthImageService import Transform3DPointsToDepthImageService
from Vision.Factories.MatcherFactory import FeatureDetectorFactory

class ReconstructionFromImages:
    def __init__(self, image01, image02, stereo_calibration, camera_a_calibration, camera_b_Calibration, gui):
        self.gui = gui
        self.image01 = image01
        self.image02 = image02
        self.calibration = stereo_calibration
        self.camera_a_calibration = camera_a_calibration
        self.camera_b_calibration = camera_b_Calibration
        self.segments = []
        self.points = []
        self.distance = 900
        self.camera_distance = 90
        logging.getLogger().setLevel(logging.INFO)

    def run(self):
        with open(self.calibration, 'r') as stereoCalibration, open(self.camera_a_calibration, 'r') as camera_a_calibration:
            try:
                initial_time = datetime.now()
                logging.info('[{}] Load Images'.format(datetime.now().time()))
                image1 = cv2.imread(self.image01)
                image2 = cv2.imread(self.image02)
                stereo_calibration_data = yaml.load(stereoCalibration, Loader=yaml.UnsafeLoader)
                camera_a_calibration_data = yaml.load(camera_a_calibration, Loader=yaml.UnsafeLoader)

                matcher_factory = FeatureDetectorFactory()

                get_matched_interest_points_from_images_service = matcher_factory.build_matcher(
                    stereo_calibration_data,
                    'freak',
                    80
                )

                logging.info('[{}] Start Match Points'.format(datetime.now().time()))
                left_points, right_points = get_matched_interest_points_from_images_service.execute(image1, image2)
                reconstructor = Reconstructor3D(stereo_calibration_data, image1, image2)

                self.points = reconstructor.execute(left_points, right_points)

                logging.info('[{}] End Match Points'.format(datetime.now().time()))

                self.generate_cameras(stereo_calibration_data)
                self.print_coordinates_reference()
                self.print_reference_plane()


                logging.info('[{}] Serve Points'.format(datetime.now().time()))
                logging.info('Total time: {}'.format(datetime.now() - initial_time))

                self.run_vision_server()

                # imager = Transform3DPointsToDepthImageService()
                # imager.execute(self.points,left_points, image1)

            except yaml.YAMLError as exc:
                print(exc)

    def run_vision_server(self):
        vision_viewer = VisionViewer()
        vision_viewer.set_points(self.points)
        vision_viewer.set_segments(self.segments)
        vision_server = VisualServer(vision_viewer)
        vision_server.run()

    def generate_cameras(self, stereoCalibrationData):
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
