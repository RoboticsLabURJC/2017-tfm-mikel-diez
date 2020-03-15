import math
import cv2
import numpy as np

from src.vision.matching.services.CalculateDistanceBetweenTwoPixelProjectionsService import CalculateDistanceBetweenTwoPixelProjectionsService


class FilterUnwantedResultsService:
    def __init__(self, calibration_data):
        self.calibration_data = calibration_data
        self.calculate_distance_between_projections_service = CalculateDistanceBetweenTwoPixelProjectionsService(calibration_data)

    def execute(self, points_a, points_b):
        points_a_filtered = []
        points_b_filtered = []
        counter = [0, 0, 0, 0, 0]

        for point_a, point_b in zip(points_a, points_b):

            distance_between_projections = self.calculate_distance_between_projections_service.execute(point_a[0], point_b[0])

            if distance_between_projections < 1:
                counter[0] += 1
            elif distance_between_projections < 1.5:
                counter[1] += 1
            elif distance_between_projections < 2:
                counter[2] += 1
            elif distance_between_projections < 3:
                counter[3] += 1
            else:
                counter[4] += 1


            if distance_between_projections < 1.5:
                points_a_filtered.append(point_a)
                points_b_filtered.append(point_b)

        print(counter)

        return np.array(points_a_filtered), np.array(points_b_filtered)
