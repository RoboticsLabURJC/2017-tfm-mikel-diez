import yaml
from Modules.Matching.imagematcher import BorderStereoMatcher
import cv2

if __name__ == '__main__':
    image1 = cv2.imread('bin/CalibrationImages/set17_reconstruction/left_image_14.png')
    image2 = cv2.imread('bin/CalibrationImages/set17_reconstruction/right_image_14.png')
    matcher = BorderStereoMatcher()
    matcher.set_images(image1, image2)
    with open("bin/CalibrationMatrix/set17/calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream)
            matcher.set_calibration_data(data)
        except yaml.YAMLError as exc:
            print(exc)

    matcher.get_matching_points()
