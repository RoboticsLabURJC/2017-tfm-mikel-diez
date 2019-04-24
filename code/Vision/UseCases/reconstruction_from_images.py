import cv2
import yaml
from Vision.Components.Matching.imagematcher import BorderStereoMatcher
from Vision.Components.Visualization.visualization import VisionViewer
from Vision.Components.Visualization.visualization_server import VisualServer
import jderobot
import logging
from datetime import datetime


class ReconstructionFromImages:
    def __init__(self, image01, image02, calibration):
        self.image01 = image01
        self.image02 = image02
        self.calibration = calibration
        self.segments = []
        self.points = []
        self.distance = 900
        self.camera_distance = 90
        logging.getLogger().setLevel(logging.INFO)

    def run(self):
        with open(self.calibration, 'r') as stream:
            try:
                initial_time = datetime.now()
                logging.info('[{}] Load Images'.format(datetime.now().time()))
                image1 = cv2.imread(self.image01)
                image2 = cv2.imread(self.image02)
                matcher = BorderStereoMatcher()
                matcher.set_images(image1, image2)
                data = yaml.load(stream)
                matcher.set_calibration_data(data)

                matcher.set_images(image1, image2)

                logging.info('[{}] Start Match Points'.format(datetime.now().time()))
                self.points = matcher.get_matching_points()

                logging.info('[{}] End Match Points'.format(datetime.now().time()))

                logging.info('[{}] Setting Points and Segments'.format(datetime.now().time()))
                self.print_cameras()
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
        distance = -(self.distance * 3.4 / self.camera_distance)
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, 50.0, distance), jderobot.Point(50.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, -50.0, distance), jderobot.Point(-50.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -50.0, distance), jderobot.Point(-50.0, 50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 50.0, distance), jderobot.Point(50.0, 50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 40.0, distance), jderobot.Point(50.0, 40.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 30.0, distance), jderobot.Point(50.0, 30.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 20.0, distance), jderobot.Point(50.0, 20.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 10.0, distance), jderobot.Point(50.0, 10.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 0.0, distance), jderobot.Point(50.0, 0.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -10.0, distance), jderobot.Point(50.0, -10.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -20.0, distance), jderobot.Point(50.0, -20.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -30.0, distance), jderobot.Point(50.0, -30.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -40.0, distance), jderobot.Point(50.0, -40.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))

        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(40.0, 50.0, distance), jderobot.Point(40.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(30.0, 50.0, distance), jderobot.Point(30.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(20.0, 50.0, distance), jderobot.Point(20.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(10.0, 50.0, distance), jderobot.Point(10.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, 50.0, distance), jderobot.Point(0.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-10.0, 50.0, distance), jderobot.Point(-10.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-20.0, 50.0, distance), jderobot.Point(-20.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-30.0, 50.0, distance), jderobot.Point(-30.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-40.0, 50.0, distance), jderobot.Point(-40.0, -50.0, distance)),
            jderobot.Color(1.0, 0.0, 0.0)))

    def print_cameras(self):
        self.points.append(jderobot.RGBPoint(-3.44965908, 1.22125194e-17, 0.0, 0.0, 0.0, 0.0))
        self.points.append(jderobot.RGBPoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
