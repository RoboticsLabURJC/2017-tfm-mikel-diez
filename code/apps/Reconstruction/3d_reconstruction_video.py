import cv2
import yaml
from src.vision.matching.services.imagematcher import BorderStereoMatcher
from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer
import jderobot

if __name__ == '__main__':
    matcher = BorderStereoMatcher()

    with open("bin/CalibrationMatrix/set140419/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            matcher.set_calibration_data(data)
            video1 = cv2.VideoCapture('bin/Videos/set140419_video/video_1.avi')
            video2 = cv2.VideoCapture('bin/Videos/set140419_video/video_2.avi')
            vision_viewer = VisionViewer()
            vision_server = VisualServer(vision_viewer)
            vision_server.run()

            while True:
                ret1, image1 = video1.read()
                ret2, image2 = video2.read()

                print('ret1: ' + str(ret1))
                print('ret2: ' + str(ret2))

                if ret1 is False or ret2 is False:
                    break


                matcher.set_images(image1, image2)

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

                vision_viewer.set_points(points)
                vision_viewer.set_segments(segments)
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
