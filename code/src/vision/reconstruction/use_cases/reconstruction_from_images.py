import logging
from datetime import datetime

import cv2
import yaml
from src.vision.reconstruction.services.Reconstruct3DPointsUsingOpenCVService import Reconstruct3DPointsUsingOpenCVService
from src.vision.matching.factories.MatcherFactory import FeatureDetectorFactory
from src.vision.presentation.factories.PresentationFactory import PresentationFactory

from src.vision.matching.services.FilterUnwantedResultsService import FilterUnwantedResultsService


class ReconstructionFromImages:
    def __init__(self, image01, image02, stereo_calibration, camera_a_calibration, camera_b_Calibration, gui):
        self.gui = gui
        self.image01 = image01
        self.image02 = image02
        self.calibration = stereo_calibration
        self.camera_a_calibration = camera_a_calibration
        self.camera_b_calibration = camera_b_Calibration
        logging.getLogger().setLevel(logging.INFO)

    def run(self):
        with open(self.calibration, 'r') as stereoCalibration:
            try:
                initial_time = datetime.now()
                logging.info('[{}] Load Images'.format(datetime.now().time()))
                image1 = cv2.imread(self.image01)
                image2 = cv2.imread(self.image02)
                stereo_calibration_data = yaml.load(stereoCalibration, Loader=yaml.UnsafeLoader)

                matcher_factory = FeatureDetectorFactory()

                get_matched_interest_points_from_images_service = matcher_factory.build_matcher(
                    stereo_calibration_data,
                    'freak',
                    80
                )

                get_filtered_points_service = FilterUnwantedResultsService(stereo_calibration_data)


                logging.info('[{}] Start Match Points'.format(datetime.now().time()))
                points_a, points_b = get_matched_interest_points_from_images_service.execute(image1, image2)
                print(points_a.shape)
                print(points_b.shape)

                points_a, points_b = get_filtered_points_service.execute(points_a, points_b)

                print(points_a.shape)
                print(points_b.shape)
                logging.info('[{}] End Match Points'.format(datetime.now().time()))

                self.gui.reconstruction_information.set_points_to_match(get_matched_interest_points_from_images_service.number_of_points_to_match)
                self.gui.reconstruction_information.set_points_matched(len(points_a))
                self.gui.reconstruction_information.set_seconds_per_point(((datetime.now() - initial_time) / get_matched_interest_points_from_images_service.number_of_points_to_match).total_seconds())
                self.gui.reconstruction_information.set_matching_time((datetime.now() - initial_time).total_seconds())

                reconstructor = Reconstruct3DPointsUsingOpenCVService(stereo_calibration_data, image1, image2)
                points = reconstructor.execute(points_a, points_b)

                logging.info('[{}] Serve Points'.format(datetime.now().time()))
                logging.info('Total time: {}'.format(datetime.now() - initial_time))

                presentation = PresentationFactory()
                presentation.build_presentation(points, points_a, image1, stereo_calibration_data, 'image')

            except yaml.YAMLError as exc:
                print(exc)
