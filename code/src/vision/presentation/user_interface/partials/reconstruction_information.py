from PyQt5 import QtWidgets
from PyQt5 import QtCore


class ReconstructionInformation(QtWidgets.QGroupBox):
    def __init__(self, parent=None):
        super(QtWidgets.QGroupBox, self).__init__(parent)
        self.setTitle('Information')
        self.parent = parent
        self.reconstruction_information_layout = QtWidgets.QVBoxLayout()
        self.reconstruction_information_layout.setAlignment(QtCore.Qt.AlignTop)

        self.points_to_match_label = QtWidgets.QLabel('Points to match: %s' % 0)
        self.points_matched_label = QtWidgets.QLabel('Points matched: %s' % 0)
        self.matching_information_seconds_per_point_label = QtWidgets.QLabel('Seconds per Point: %s' % 0)
        self.matching_information_total_matching_seconds_label = QtWidgets.QLabel('Matching time (s): %s' % 0)

        self.reconstruction_information_layout.addWidget(self.points_to_match_label)
        self.reconstruction_information_layout.addWidget(self.points_matched_label)
        self.reconstruction_information_layout.addWidget(self.matching_information_seconds_per_point_label)
        self.reconstruction_information_layout.addWidget(self.matching_information_total_matching_seconds_label)

        self.setLayout(self.reconstruction_information_layout)

    def set_points_to_match(self, value):
        self.points_to_match_label.setText(
            'Points to match: %s' % value
        )

    def set_points_matched(self, value):
        self.points_matched_label.setText(
            'Points matched: %s' % value
        )

    def set_seconds_per_point(self, value):
        self.matching_information_seconds_per_point_label.setText(
            'Seconds per Point: %s' % value
        )

    def set_matching_time(self, value):
        self.matching_information_total_matching_seconds_label.setText(
            'Matching time (s): %s' % value
        )