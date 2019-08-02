import cv2
import yaml
from src.vision.matching.services.imagematcher import BorderStereoMatcher
from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer
import jderobot

class ReconstructionFromVideo:
    def __init__(self, video1, video2, calibration):
        self.video1 = video1
        self.video2 = video2
        self.calibration = calibration
        self.segments = []
        self.points = []

    def run(self):
        matcher = BorderStereoMatcher()

        with open(self.calibration, 'r') as stream:
            try:
                data = yaml.load(stream)
                matcher.set_calibration_data(data)
                video1 = cv2.VideoCapture(self.video1)
                video2 = cv2.VideoCapture(self.video2)
                vision_viewer = VisionViewer()
                vision_server = VisualServer(vision_viewer)
                vision_server.run()

                print(self.video1)
                print(self.video2)

                while True:
                    ret1, image1 = video1.read()
                    ret2, image2 = video2.read()



                    if ret1 is False or ret2 is False:
                        print('there is a problem with the videos')
                        break

                    matcher.set_images(image1, image2)

                    # self.points = matcher.get_matching_points()
                    self.print_cameras()
                    self.print_coordinates_reference()
                    self.print_reference_plane()

                    vision_viewer.set_points(self.points)
                    vision_viewer.set_segments(self.segments)

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
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, 50.0, -55.0), jderobot.Point(50.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, -50.0, -55.0), jderobot.Point(-50.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -50.0, -55.0), jderobot.Point(-50.0, 50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 50.0, -55.0), jderobot.Point(50.0, 50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 40.0, -55.0), jderobot.Point(50.0, 40.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 30.0, -55.0), jderobot.Point(50.0, 30.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 20.0, -55.0), jderobot.Point(50.0, 20.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 10.0, -55.0), jderobot.Point(50.0, 10.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, 0.0, -55.0), jderobot.Point(50.0, 0.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -10.0, -55.0), jderobot.Point(50.0, -10.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -20.0, -55.0), jderobot.Point(50.0, -20.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -30.0, -55.0), jderobot.Point(50.0, -30.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, -40.0, -55.0), jderobot.Point(50.0, -40.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))

        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(40.0, 50.0, -55.0), jderobot.Point(40.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(30.0, 50.0, -55.0), jderobot.Point(30.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(20.0, 50.0, -55.0), jderobot.Point(20.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(10.0, 50.0, -55.0), jderobot.Point(10.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, 50.0, -55.0), jderobot.Point(0.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-10.0, 50.0, -55.0), jderobot.Point(-10.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-20.0, 50.0, -55.0), jderobot.Point(-20.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-30.0, 50.0, -55.0), jderobot.Point(-30.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        self.segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-40.0, 50.0, -55.0), jderobot.Point(-40.0, -50.0, -55.0)),
            jderobot.Color(1.0, 0.0, 0.0)))

    def print_cameras(self):
        self.points.append(jderobot.RGBPoint(3.44965908, 1.22125194e-17, 0.0, 0.0, 0.0, 0.0))
        self.points.append(jderobot.RGBPoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
