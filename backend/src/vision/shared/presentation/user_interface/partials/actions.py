from PyQt5 import QtWidgets
from PyQt5 import QtCore

import os
import cv2

from src.vision.reconstruction.use_cases.reconstruction_from_video import ReconstructionFromVideo
from src.vision.reconstruction.use_cases.reconstruction_from_images import ReconstructionFromImages
from src.vision.calibration.use_cases.CalibrateStereoCamerasFromChessboard import CalibrateStereoCamerasFromChessboard
from src.vision.reconstruction.use_cases.reconstruction_cameras_from_calibration import RecontructCameras

from src.vision.presentation.user_interface.partials.calibration_information import CalibrationInformation
from src.vision.presentation.user_interface.partials.reconstruction_information import ReconstructionInformation


class Actions(QtWidgets.QTabWidget):
    take_calibration_images = False
    calibration_images_taken = 0
    frames_between_calibration_images = 0

    def __init__(self, parent=None):
        super(QtWidgets.QTabWidget, self).__init__(parent)
        self.parent = parent

        self.resize(325, 525)
        self.move(920, 100)

        self.addTab(self.create_calibration_widget(), 'Calibration')
        self.addTab(self.create_reconstruction_widget(), 'Reconstruction')

    def create_calibration_widget(self):
        self.calibration_actions = QtWidgets.QGroupBox('Actions')
        self.calibration_actions_layout = QtWidgets.QVBoxLayout()
        self.calibration_actions_layout.setAlignment(QtCore.Qt.AlignTop)
        self.calibration_actions_layout.addWidget(self.create_calibration_images_button())
        self.calibration_actions_layout.addWidget(self.create_calibrate_cameras_button())
        self.calibration_actions_layout.addWidget(self.create_build_cameras_button())

        self.calibration_actions.setLayout(self.calibration_actions_layout)

        self.calibration_information = CalibrationInformation()

        self.calibration_widget = QtWidgets.QWidget()
        self.calibration_widget_layout = QtWidgets.QVBoxLayout()
        self.calibration_widget_layout.addWidget(self.calibration_actions)
        self.calibration_widget_layout.addWidget(self.calibration_information)

        self.calibration_widget.setLayout(self.calibration_widget_layout)

        return self.calibration_widget

    def create_reconstruction_widget(self):
        reconstruction_actions = QtWidgets.QGroupBox('Actions')
        reconstruction_actions_layout = QtWidgets.QVBoxLayout()
        reconstruction_actions_layout.setAlignment(QtCore.Qt.AlignTop)
        reconstruction_actions_layout.addWidget(self.create_take_photo_button())
        reconstruction_actions_layout.addWidget(self.create_video_record_button())
        reconstruction_actions_layout.addWidget(self.create_reconstruction_button())
        reconstruction_actions_layout.addWidget(self.create_reconstruction_from_video_button())

        self.reconstruction_information = ReconstructionInformation()

        reconstruction_actions.setLayout(reconstruction_actions_layout)
        reconstruction_actions_widget = QtWidgets.QWidget()
        reconstruction_widget_layout = QtWidgets.QVBoxLayout()
        reconstruction_widget_layout.addWidget(reconstruction_actions)
        reconstruction_widget_layout.addWidget(self.reconstruction_information)

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
        stereo_calibrator = CalibrateStereoCamerasFromChessboard()
        stereo_calibrator.execute(self.parent.combobox_selector.currentText())

    def show_cameras(self):
        calibration_file = self.parent.configuration.general_configuration.sets_folder + self.parent.combobox_selector.currentText() + '/calibrated_camera.yml'
        reconstructor = RecontructCameras(calibration_file)
        reconstructor.run()

    def toggle_take_calibration_images(self):
        self.calibration_images_taken = 0
        self.take_calibration_images = not self.take_calibration_images

    def should_take_calibration_images(self):
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

    def take_calibration_image(self):
        self.frames_between_calibration_images += 1
        if self.frames_between_calibration_images == 100:
            if not os.path.exists('bin/sets/' + self.parent.combobox_selector.currentText() + '/calibration_images'):
                os.makedirs('bin/sets/' + self.parent.combobox_selector.currentText() + '/calibration_images')


            print('Take Dual Image ' + str(self.calibration_images_taken))

            print('::Write Left Image::')
            im_left = self.parent.cameras[0].get_image_hd()
            cv2.imwrite('bin/sets/' + self.parent.combobox_selector.currentText() + '/calibration_images/left_image_' + str(self.calibration_images_taken) + '.png',
                        im_left)

            print('::Write Right Image::')
            im_right = self.parent.cameras[1].get_image_hd()
            cv2.imwrite('bin/sets/' + self.parent.combobox_selector.currentText() + '/calibration_images/right_image_' + str(self.calibration_images_taken) + '.png',
                        im_right)
            self.frames_between_calibration_images = 0
            self.update_calibration_images_amount()

    def update_calibration_images_amount(self):
        self.calibration_images_taken += 1
        self.calibration_information.set_calibration_images_taken(self.calibration_images_taken)

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

        #self.photos_taken += 1
        #print('Take Dual Image ' + str(self.photos_taken))

        print('::Write Left Image::')
        im_left = self.parent.cameras[0].get_image_hd()
        # im_rgb_left = cv2.cvtColor(cv2.resize(im_left,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.parent.combobox_selector.currentText() + '/images/left_image_2.png', im_left)

        print('::Write Right Image::')
        im_right = self.parent.cameras[1].get_image_hd()
        # im_rgb_right = cv2.cvtColor(cv2.resize(im_right,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.parent.combobox_selector.currentText() + '/images/right_image_2.png', im_right)

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
