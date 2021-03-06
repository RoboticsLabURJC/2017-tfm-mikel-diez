import cv2
import yaml
from src.vision.matching.services.imagematcher import BorderStereoMatcher
from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer
import jderobot
import time

if __name__ == '__main__':
    image1 = cv2.imread('bin/CalibrationImages/setqwe/left_image_1.png')
    image2 = cv2.imread('bin/CalibrationImages/setqwe/right_image_1.png')
    matcher = BorderStereoMatcher()
    matcher.set_images(image1, image2)
    with open("bin/CalibrationMatrix/set140419/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            matcher.set_calibration_data(data)
            points = matcher.get_matching_points()
            points.append(jderobot.RGBPoint(3.44965908, 1.22125194e-17, 0.0, 0.0, 0.0, 0.0))
            points.append(jderobot.RGBPoint(0.0, 0.0, 0.0, 0.0, 0.0, 0.0))
            segments = [
                jderobot.RGBSegment(jderobot.Segment(jderobot.Point(10.0, 0.0, 0.0), jderobot.Point(0.0, 0.0, 0.0)),
                                    jderobot.Color(1.0, 0.0, 0.0)),
                jderobot.RGBSegment(jderobot.Segment(jderobot.Point(0.0, 10.0, 0.0), jderobot.Point(0.0, 0.0, 0.0)),
                                    jderobot.Color(0.0, 1.0, 0.0)),
                jderobot.RGBSegment(jderobot.Segment(jderobot.Point(0.0, 0.0, 10.0), jderobot.Point(0.0, 0.0, 0.0)),
                                    jderobot.Color(0.0, 0.0, 1.0))
            ]

            segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(50.0, 50.0, -55.0), jderobot.Point(50.0, -50.0, -55.0)),
                jderobot.Color(1.0, 0.0, 0.0)))
            segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(50.0, -50.0, -55.0), jderobot.Point(-50.0, -50.0, -55.0)),
                jderobot.Color(1.0, 0.0, 0.0)))
            segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(-50.0, -50.0, -55.0), jderobot.Point(-50.0, 50.0, -55.0)),
                jderobot.Color(1.0, 0.0, 0.0)))
            segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(-50.0, 50.0, -55.0), jderobot.Point(50.0, 50.0, -55.0)),
                jderobot.Color(1.0, 0.0, 0.0)))

            vision_viewer = VisionViewer()
            vision_viewer.set_points(points)
            vision_viewer.set_segments(segments)
            vision_server = VisualServer(vision_viewer)
            vision_server.run()
            #
            # for times in range(0, 255):
            #     points = [
            #         jderobot.RGBPoint(0.0 + float(times), 0.0, 0.0, 0.0, 0.0, 0.0)
            #     ]
            #     vision_viewer.set_points(points)
            #     print(times)
            #     print(points)
            #     time.sleep(3)

        except yaml.YAMLError as exc:
            print(exc)
