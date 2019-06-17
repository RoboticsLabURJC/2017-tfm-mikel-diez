import cv2
import yaml
import numpy as np

from Vision.Components.Reconstruction.Reconstructor3D import Reconstructor3D
from Vision.Services.Matching.MatchInterestPointsWithOrb import MatchInterestPointsWithOrb


if __name__ == '__main__':
    image_a = cv2.imread('bin/sets/set_10y_center/images/left_image_1.png')
    image_b = cv2.imread('bin/sets/set_10y_center/images/right_image_1.png')

    with open("bin/sets/set_10y_center/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream, Loader=yaml.UnsafeLoader)

            matcher = MatchInterestPointsWithOrb(data)
            points_left, points_right = matcher.execute(image_a, image_b)

            reconstructor = Reconstructor3D(data, image_a, image_b)

            points = reconstructor.execute(points_left, points_right)

        except yaml.YAMLError as exc:
            print(exc)





