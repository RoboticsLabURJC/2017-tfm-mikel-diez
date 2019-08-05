from PyQt5 import QtWidgets


class Options(QtWidgets.QTabWidget):
    def __init__(self, parent=None):
        super(QtWidgets.QTabWidget, self).__init__(parent)
        self.parent = parent
        self.resize(850, 250)
        self.move(50, 375)

        calibration_options = QtWidgets.QWidget()
        matching_options = QtWidgets.QWidget()
        reconstruction_options = QtWidgets.QWidget()
        presentation_options = QtWidgets.QWidget()
        self.addTab(calibration_options, 'Calibration')
        self.addTab(matching_options, 'Matching')
        self.addTab(reconstruction_options, 'Reconstruction')
        self.addTab(presentation_options, 'Presentation')

        matching_options.layout = QtWidgets.QHBoxLayout()

        color_spaces_group = QtWidgets.QGroupBox('Color Space')
        color_spaces_vertical_layour = QtWidgets.QVBoxLayout()
        bgr_color_space_radio_button = QtWidgets.QRadioButton('BGR')
        hsv_color_space_radio_button = QtWidgets.QRadioButton('HSV')
        grays_color_space_radio_button = QtWidgets.QRadioButton('Grays')
        hsv_color_space_radio_button.setChecked(True)
        color_spaces_vertical_layour.addWidget(bgr_color_space_radio_button)
        color_spaces_vertical_layour.addWidget(hsv_color_space_radio_button)
        color_spaces_vertical_layour.addWidget(grays_color_space_radio_button)
        color_spaces_group.setLayout(color_spaces_vertical_layour)

        image_size_group = QtWidgets.QGroupBox('Image Size')
        image_size_vertical_layour = QtWidgets.QVBoxLayout()
        image_size_1280_720_radio_button = QtWidgets.QRadioButton('1280x720')
        image_size_960_540_radio_button = QtWidgets.QRadioButton('960x540')
        image_size_640_480_radio_button = QtWidgets.QRadioButton('640x480')
        image_size_960_540_radio_button.setChecked(True)
        image_size_vertical_layour.addWidget(image_size_1280_720_radio_button)
        image_size_vertical_layour.addWidget(image_size_960_540_radio_button)
        image_size_vertical_layour.addWidget(image_size_640_480_radio_button)
        image_size_group.setLayout(image_size_vertical_layour)

        epipolar_range_group = QtWidgets.QGroupBox('Ranges')
        epipolar_range_vertical_layout = QtWidgets.QVBoxLayout()
        epiline_range_combobox_selector = QtWidgets.QComboBox()
        epiline_range_combobox_selector.addItems(['Epiline Range', '1', '2', '3', '4', '5'])
        patch_size_combobox_selector = QtWidgets.QComboBox()
        patch_size_combobox_selector.addItems(['Patch Size', '5', '10', '20', '30', '40'])
        epipolar_range_vertical_layout.addWidget(epiline_range_combobox_selector)
        epipolar_range_vertical_layout.addWidget(patch_size_combobox_selector)
        epipolar_range_group.setLayout(epipolar_range_vertical_layout)

        matching_options.layout.addWidget(color_spaces_group)
        matching_options.layout.addWidget(image_size_group)
        matching_options.layout.addWidget(epipolar_range_group)
        matching_options.setLayout(matching_options.layout)
