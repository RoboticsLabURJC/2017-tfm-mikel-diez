import yaml
from Vision.Factories.PresentationFactory import PresentationFactory

class RecontructCameras:
    def __init__(self, stereo_calibration):
        self.calibration = stereo_calibration

    def run(self):
        with open(self.calibration, 'r') as stereoCalibration:
            try:
                stereo_calibration_data = yaml.load(stereoCalibration, Loader=yaml.UnsafeLoader)

                presentation = PresentationFactory()
                presentation.build_presentation([], [], None, stereo_calibration_data, 'd3')

            except yaml.YAMLError as exc:
                print(exc)
