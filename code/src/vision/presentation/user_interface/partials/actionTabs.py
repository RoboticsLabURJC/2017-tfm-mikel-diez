from PyQt5 import QtWidgets
from PyQt5 import QtCore

import os
import cv2

from src.vision.reconstruction.use_cases.reconstruction_from_video import ReconstructionFromVideo
from src.vision.reconstruction.use_cases.reconstruction_from_images import ReconstructionFromImages
from src.vision.calibration.use_cases.stereo_calibration_from_chessboard import StereoCalibrationFromChessboard
from src.vision.reconstruction.use_cases.reconstruction_cameras_from_calibration import RecontructCameras


class ActionTabs(QtWidgets.QTabWidget):
    take_calibration_images = False

    def __init__(self, parent=None):
        super(QtWidgets.QTabWidget, self).__init__(parent)
        self.parent = parent

        self.resize(325, 525)
        self.move(920, 100)

        self.addTab(self.create_calibration_widget(), 'Calibration')
        self.addTab(self.create_reconstruction_widget(), 'Reconstruction')

    def create_calibration_widget(self):
        calibration_actions = QtWidgets.QGroupBox('Actions')
        calibration_actions_layout = QtWidgets.QVBoxLayout()
        calibration_actions_layout.setAlignment(QtCore.Qt.AlignTop)
        calibration_actions_layout.addWidget(self.create_calibrate_cameras_button())
        calibration_actions_layout.addWidget(self.create_calibration_images_button())
        calibration_actions_layout.addWidget(self.create_build_cameras_button())

        calibration_information = QtWidgets.QGroupBox('Information')
        calibration_information_layout = QtWidgets.QVBoxLayout()
        calibration_information_layout.setAlignment(QtCore.Qt.AlignTop)

        calibration_actions.setLayout(calibration_actions_layout)
        calibration_information.setLayout(calibration_information_layout)

        calibration_widget = QtWidgets.QWidget()
        calibration_widget_layout = QtWidgets.QVBoxLayout()
        calibration_widget_layout.addWidget(calibration_actions)
        calibration_widget_layout.addWidget(calibration_information)

        calibration_widget.setLayout(calibration_widget_layout)

        return calibration_widget

    def create_reconstruction_widget(self):
        reconstruction_actions = QtWidgets.QGroupBox('Actions')
        reconstruction_actions_layout = QtWidgets.QVBoxLayout()
        reconstruction_actions_layout.setAlignment(QtCore.Qt.AlignTop)
        reconstruction_actions_layout.addWidget(self.create_take_photo_button())
        reconstruction_actions_layout.addWidget(self.create_video_record_button())
        reconstruction_actions_layout.addWidget(self.create_reconstruction_button())
        reconstruction_actions_layout.addWidget(self.create_reconstruction_from_video_button())

        reconstruction_information = QtWidgets.QGroupBox('Information')
        reconstruction_information_layout = QtWidgets.QVBoxLayout()

        self.matching_information_points_to_match_label = QtWidgets.QLabel('Points to match: %s' % 0)
        self.matching_information_points_matched_label = QtWidgets.QLabel('Points matched: %s' % 0)
        self.matching_information_seconds_per_point_label = QtWidgets.QLabel('Seconds per Point: %s' % 0)
        self.matching_information_total_matching_seconds_label = QtWidgets.QLabel('Matching time (s): %s' % 0)


        reconstruction_information_layout.addWidget(self.matching_information_points_to_match_label)
        reconstruction_information_layout.addWidget(self.matching_information_points_matched_label)
        reconstruction_information_layout.addWidget(self.matching_information_seconds_per_point_label)
        reconstruction_information_layout.addWidget(self.matching_information_total_matching_seconds_label)


        reconstruction_actions.setLayout(reconstruction_actions_layout)
        reconstruction_information.setLayout(reconstruction_information_layout)


        reconstruction_actions_widget = QtWidgets.QWidget()
        reconstruction_widget_layout = QtWidgets.QVBoxLayout()
        reconstruction_widget_layout.addWidget(reconstruction_actions)
        reconstruction_widget_layout.addWidget(reconstruction_information)

        reconstruction_actions_widget.setLayout(reconstruction_widget_layout)

        return reconstruction_actions_widget

    def create_calibrate_cameras_button(self):
        calibrate_button = QtWidgets.QPushButton('Calibrate Cameras', self)
        calibrate_button.resize(150, 40)
        calibrate_button.clicked.connect(self.calibrate_set)

        return calibrate_button

    def create_calibration_images_button(self):
        take_calibration_images = QtWidgets.QPushButton('Get Calibration Set', self)
        take_calibration_images.setCheckable(True)
        take_calibration_images.resize(150, 40)

        take_calibration_images.clicked.connect(self.toggle_take_calibration_images)

        return take_calibration_images

    def create_build_cameras_button(self):
        build_cameras_button = QtWidgets.QPushButton('Show Cameras', self)
        build_cameras_button.resize(150, 40)
        build_cameras_button.clicked.connect(self.show_cameras)

        return build_cameras_button

    def calibrate_set(self):
        stereo_calibrator = StereoCalibrationFromChessboard()
        stereo_calibrator.execute(self.parent.combobox_selector.currentText())

    def show_cameras(self):
        calibration_file = self.parent.configuration.general_configuration.sets_folder + self.parent.combobox_selector.currentText() + '/calibrated_camera.yml'
        reconstructor = RecontructCameras(calibration_file)
        reconstructor.run()

    def toggle_take_calibration_images(self):
        self.take_calibration_images = not self.take_calibration_images

    def is_take_calibration_images_checked(self):
        return self.take_calibration_images

    def create_reconstruction_button(self):
        reconstruction = QtWidgets.QWidget()
        reconstruction_layout = QtWidgets.QHBoxLayout()
        reconstruction_layout.setContentsMargins(0, 0, 0, 0)

        reconstruction_button = QtWidgets.QPushButton('Rec. Image', self)
        reconstruction_button.clicked.connect(self.reconstruct_from_images)
        images = [str(number) for number in range(6)]
        self.reconstruction_image_selector = QtWidgets.QComboBox(self)
        self.reconstruction_image_selector.addItems(images)

        reconstruction_layout.addWidget(reconstruction_button)
        reconstruction_layout.addWidget(self.reconstruction_image_selector)
        reconstruction.setLayout(reconstruction_layout)

        return reconstruction

    def create_reconstruction_from_video_button(self):
        reconstruction_button = QtWidgets.QPushButton('Rec. Video', self)
        reconstruction_button.move(1090, 200)
        reconstruction_button.resize(150, 40)
        reconstruction_button.clicked.connect(self.reconstruct_from_video)

        return reconstruction_button

    def create_take_photo_button(self):
        take_photo_button = QtWidgets.QPushButton('Take Photo', self)
        take_photo_button.move(925, 150)
        take_photo_button.resize(150, 40)
        take_photo_button.clicked.connect(self.take_photo)

        return take_photo_button

    def create_video_record_button(self):
        record_video_button = QtWidgets.QPushButton('Record Video', self)
        record_video_button.setCheckable(True)
        record_video_button.move(1090, 150)
        record_video_button.resize(150, 40)
        record_video_button.clicked.connect(self.record_video)

        return record_video_button

    def record_video(self):
        if not os.path.exists('bin/Videos/' + self.textbox.text() + '_video'):
            os.makedirs('bin/Videos/' + self.textbox.text() + '_video')

        if self.video_recorder_1 is None:
            print('->Create video recorder<-')
            self.video_recorder_1 = cv2.VideoWriter(
                'bin/Videos/' + self.textbox.text() + '_video/video_1.avi',
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                10,
                (1280, 720)
            )

            self.video_recorder_2 = cv2.VideoWriter(
                'bin/Videos/' + self.textbox.text() + '_video/video_2.avi',
                cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                10,
                (1280, 720)
            )

        if self.record_video_button.isChecked() is False:
            self.video_recorder_1.release()
            self.video_recorder_2.release()

            self.video_recorder_1 = None
            self.video_recorder_2 = None

        self.should_record_video = self.record_video_button.isChecked()

    def take_photo(self):
        if not os.path.exists('bin/sets/' + self.parent.combobox_selector.currentText()):
            os.makedirs('bin/sets/' + self.parent.combobox_selector.currentText())

        if not os.path.exists('bin/sets/' + self.parent.combobox_selector.currentText() + '/images'):
            os.makedirs('bin/sets/' + self.parent.combobox_selector.currentText() + '/images')

        self.photos_taken += 1
        print('Take Dual Image ' + str(self.photos_taken))

        print('::Write Left Image::')
        im_left = self.parent.cameras[0].get_image_hd()
        # im_rgb_left = cv2.cvtColor(cv2.resize(im_left,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.parent.combobox_selector.currentText() + '/images/left_image_' + str(
            self.photos_taken) + '.png', im_left)

        print('::Write Right Image::')
        im_right = self.parent.cameras[1].get_image_hd()
        # im_rgb_right = cv2.cvtColor(cv2.resize(im_right,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.parent.combobox_selector.currentText() + '/images/right_image_' + str(
            self.photos_taken) + '.png', im_right)

        self.images_counter.setNum(self.photos_taken)

    def reconstruct_from_video(self):
        video_reconstructor = ReconstructionFromVideo(
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/videos/video_1.avi',
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/videos/video_2.avi',
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/calibrated_camera.yml'
        )
        video_reconstructor.run()

    def reconstruct_from_images(self):
        images_reconstructor = ReconstructionFromImages(
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/images/left_image_' + self.reconstruction_image_selector.currentText() + '.png',
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/images/right_image_' + self.reconstruction_image_selector.currentText() + '.png',
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/calibrated_camera.yml',
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/camera_A_calibration.yml',
            'bin/sets/' + self.parent.combobox_selector.currentText() + '/camera_B_calibration.yml',
            self
        )
        images_reconstructor.run()
