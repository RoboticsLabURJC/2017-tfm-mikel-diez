from PyQt5 import QtWidgets
from PyQt5 import QtCore


class CalibrationInformation(QtWidgets.QGroupBox):
    sets_folder = None
    calibration_images_taken = None

    def __init__(self, parent=None):
        super(QtWidgets.QGroupBox, self).__init__(parent)
        self.setTitle('Information')
        self.parent = parent
        self.calibration_information_layout = QtWidgets.QVBoxLayout()
        self.calibration_information_layout.setAlignment(QtCore.Qt.AlignTop)

        self.set_path_label = QtWidgets.QLabel('Path: %s' % self.sets_folder)
        self.calibration_images_taken_label = QtWidgets.QLabel('Images Taken: %s' % self.calibration_images_taken)

        self.calibration_information_layout.addWidget(self.set_path_label)
        self.calibration_information_layout.addWidget(self.calibration_images_taken_label)

        self.setLayout(self.calibration_information_layout)

    def set_calibration_images_taken(self, value):
        self.calibration_images_taken = value
        self.calibration_images_taken_label.setText(
            'Images Taken: %s' % self.calibration_images_taken
        )

    def set_current_folder(self, path):
        self.sets_folder = path
        self.set_path_label.setText(
            'Path: %s' % self.sets_folder
        )