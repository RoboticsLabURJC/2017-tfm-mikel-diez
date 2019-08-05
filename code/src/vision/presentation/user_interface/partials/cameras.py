from PyQt5 import QtWidgets
from PyQt5 import QtCore

import os
import cv2

from src.vision.reconstruction.use_cases.reconstruction_from_video import ReconstructionFromVideo
from src.vision.reconstruction.use_cases.reconstruction_from_images import ReconstructionFromImages
from src.vision.calibration.use_cases.stereo_calibration_from_chessboard import StereoCalibrationFromChessboard
from src.vision.reconstruction.use_cases.reconstruction_cameras_from_calibration import RecontructCameras


class Cameras(QtWidgets.QTabWidget):

    def __init__(self, cameras, parent=None):
        super(QtWidgets.QTabWidget, self).__init__(parent)
        self.cameras = cameras
        self.parent = parent

