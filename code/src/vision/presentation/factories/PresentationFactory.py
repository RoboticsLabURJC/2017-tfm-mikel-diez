import numpy as np
import jderobot

from src.vision.presentation.servers.visualization import VisionViewer
from src.vision.presentation.servers.visualization_server import VisualServer
from src.vision.presentation.services.Transform3DPointsToDepthImageService import Transform3DPointsToDepthImageService
from src.vision.presentation.services.Transform3DPointsToRigDepthImageService import Transform3DPointsToRigDepthImageService
from src.vision.presentation.services.Transform3DPointsToDepthFileService import Transform3DPointsToDepthFileService

from src.vision.presentation.services.GetCameraRepresentationWithRotationAndTranslationService import \
    GetCameraRepresentationWithRotationAndTranslationService


class PresentationFactory:
    presentation = {
        'd3': 'build_3d_server',
        'image': 'build_depth_image',
        'file': 'build_depth_file',
        'imageD' : 'build_rig_depth_image'
    }

    def build_presentation(self, points_3d, points_2d, image, calibration_data, presentation_type='d3'):
        method_name = self.presentation[presentation_type]
        matcher = getattr(self, method_name, lambda: 'Invalid')
        return matcher(points_3d, points_2d, image, calibration_data)

    def build_3d_server(self, points_3d, points_2d, image, calibration_data):
        segments = []
        segments = self.generate_cameras(calibration_data, segments)
        segments = self.print_coordinates_reference(segments)
        segments = self.print_reference_plane(segments)
        vision_viewer = VisionViewer()
        vision_viewer.set_points(points_3d)
        vision_viewer.set_segments(segments)
        vision_server = VisualServer(vision_viewer)
        vision_server.run()

    @staticmethod
    def build_depth_image(points_3d, points_2d, image, calibration_data):
        imager = Transform3DPointsToDepthImageService()
        imager.execute(points_3d, points_2d, image)

    @staticmethod
    def build_rig_depth_image(points_3d, points_2d, image, calibration_data):
        imager = Transform3DPointsToRigDepthImageService()
        imager.execute(points_3d, calibration_data)

    def build_depth_file(self, points_3d, points_2d, image, calibration_data):
        imager = Transform3DPointsToDepthFileService()
        imager.execute(points_3d, points_2d, calibration_data, image)

    @staticmethod
    def generate_cameras(stereo_calibration_data, segments):
        camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
        segments += camera_generator.execute(
            np.array(stereo_calibration_data['cameraMatrix2']),
            np.array(stereo_calibration_data['distCoeffs2']),
            np.array(stereo_calibration_data['r2']),
            np.array(stereo_calibration_data['p2']),
            np.array(stereo_calibration_data['R']),
            np.array(stereo_calibration_data['T'])
        )
        camera_generator = GetCameraRepresentationWithRotationAndTranslationService()
        segments += camera_generator.execute(
            np.array(stereo_calibration_data['cameraMatrix1']),
            np.array(stereo_calibration_data['distCoeffs1']),
            np.array(stereo_calibration_data['r1']),
            np.array(stereo_calibration_data['p1']),
            np.identity(3),
            np.array([.0, .0, .0])
        )
        return segments

    @staticmethod
    def print_coordinates_reference(segments):
        segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(10.0, 0.0, 0.0), jderobot.Point(0.0, 0.0, 0.0)),
                jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(0.0, 10.0, 0.0), jderobot.Point(0.0, 0.0, 0.0)),
                jderobot.Color(0.0, 1.0, 0.0)))
        segments.append(jderobot.RGBSegment(
                jderobot.Segment(jderobot.Point(0.0, 0.0, 10.0), jderobot.Point(0.0, 0.0, 0.0)),
                jderobot.Color(0.0, 0.0, 1.0)))

        return segments

    @staticmethod
    def print_reference_plane(segments):
        distance = (900 * 3.4 / 90)
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, distance, 50.0), jderobot.Point(50.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(50.0, distance, -50.0), jderobot.Point(-50.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -50.0), jderobot.Point(-50.0, distance, 50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 50.0), jderobot.Point(50.0, distance, 50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 40.0), jderobot.Point(50.0, distance, 40.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 30.0), jderobot.Point(50.0, distance, 30.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 20.0), jderobot.Point(50.0, distance, 20.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 10.0), jderobot.Point(50.0, distance, 10.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, 0.0), jderobot.Point(50.0,  distance, 0.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -10.0), jderobot.Point(50.0, distance, -10.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -20.0), jderobot.Point(50.0, distance, -20.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -30.0), jderobot.Point(50.0, distance, -30.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-50.0, distance, -40.0), jderobot.Point(50.0, distance, -40.0)),
            jderobot.Color(1.0, 0.0, 0.0)))

        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(40.0, distance, 50.0), jderobot.Point(40.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(30.0, distance, 50.0), jderobot.Point(30.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(20.0, distance, 50.0), jderobot.Point(20.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(10.0, distance, 50.0), jderobot.Point(10.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(0.0, distance, 50.0), jderobot.Point(0.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-10.0, distance, 50.0), jderobot.Point(-10.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-20.0, distance, 50.0), jderobot.Point(-20.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-30.0, distance, 50.0), jderobot.Point(-30.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))
        segments.append(jderobot.RGBSegment(
            jderobot.Segment(jderobot.Point(-40.0, distance, 50.0), jderobot.Point(-40.0, distance, -50.0)),
            jderobot.Color(1.0, 0.0, 0.0)))

        return segments
