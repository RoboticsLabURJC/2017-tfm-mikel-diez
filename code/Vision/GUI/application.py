from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Vision.UseCases.reconstruction_from_video import ReconstructionFromVideo
from Vision.UseCases.reconstruction_from_images import ReconstructionFromImages
from Vision.UseCases.stereo_calibration_from_chessboard import StereoCalibrationFromChessboard
from Vision.UseCases.reconstruction_cameras_from_calibration import RecontructCameras

import os
import cv2

import numpy as np

class Application(QtWidgets.QWidget):
    
    updGUI = QtCore.pyqtSignal()
    photos_taken = 0
    frames = 0
    counter = 0

    def __init__(self, parent=None):
        self.cameras = None

        self.create_main_window(parent)

        self.create_left_image()
        self.create_right_image()
        self.create_take_photo_button()
        self.create_calibration_images_button()
        self.create_calibrate_cameras_button()
        self.create_reconstruction_button()
        self.create_reconstruction_from_video_button()
        self.create_input_textbox()
        self.create_new_folder_button()
        self.create_image_counter_text()
        self.create_video_record_button()
        self.create_combobox_selector()
        self.create_matching_options_group()
        self.create_options_tabs()
        self.create_information_tabs()
        self.create_build_cameras_button()

        self.video_recorder_1 = None
        self.video_recorder_2 = None
        self.should_record_video = False

        self.video_capture1 = cv2.VideoCapture(1)
        self.video_capture2 = cv2.VideoCapture(2)

    def create_image_counter_text(self):
        self.images_counter = QtWidgets.QLabel(self)
        self.images_counter.resize(150, 40)
        self.images_counter.move(925, 250)
        self.images_counter.setAlignment(QtCore.Qt.AlignCenter)
        self.images_counter.setFont(QtGui.QFont('Arial', 35))
        self.images_counter.setNum(0)
        self.images_counter.show()

    def create_input_textbox(self):
        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.move(925, 50)
        self.textbox.resize(110, 40)

    def create_new_folder_button(self):
        self.new_folder_button_icon = QtGui.QIcon.fromTheme('edit-undo', QtGui.QIcon('resources/icons/new-folder.png'))
        self.new_folder_button = QtWidgets.QPushButton('', self)
        self.new_folder_button.move(1035, 50)
        self.new_folder_button.resize(40, 40)
        self.new_folder_button.setIcon(self.new_folder_button_icon)
        self.new_folder_button.setIconSize(QtCore.QSize(24, 24))
        self.new_folder_button.clicked.connect(self.create_new_set)

    def create_reconstruction_button(self):
        self.reconstruction_button = QtWidgets.QPushButton('Reconst. from Image', self)
        self.reconstruction_button.move(925, 200)
        self.reconstruction_button.resize(150, 40)
        self.reconstruction_button.clicked.connect(self.reconstruct_from_images)

    def create_reconstruction_from_video_button(self):
        self.reconstruction_button = QtWidgets.QPushButton('Reconst. from Video', self)
        self.reconstruction_button.move(1090, 200)
        self.reconstruction_button.resize(150, 40)
        self.reconstruction_button.clicked.connect(self.reconstruct_from_video)

    def create_build_cameras_button(self):
        self.build_cameras_button = QtWidgets.QPushButton('Show Cameras', self)
        self.build_cameras_button.move(1090, 250)
        self.build_cameras_button.resize(150, 40)
        self.build_cameras_button.clicked.connect(self.show_cameras)

    def create_calibrate_cameras_button(self):
        self.calibrate_button = QtWidgets.QPushButton('Calibrate Cameras', self)
        self.calibrate_button.move(1090, 100)
        self.calibrate_button.resize(150, 40)
        self.calibrate_button.clicked.connect(self.calibrate_set)

    def create_calibration_images_button(self):
        self.take_calibration_images = QtWidgets.QPushButton('Get Calibration Set', self)
        self.take_calibration_images.setCheckable(True)
        self.take_calibration_images.move(925, 100)
        self.take_calibration_images.resize(150, 40)

    def create_take_photo_button(self):
        self.take_photo_button = QtWidgets.QPushButton('Take Photo', self)
        self.take_photo_button.move(925, 150)
        self.take_photo_button.resize(150, 40)
        self.take_photo_button.clicked.connect(self.take_photo)

    def create_video_record_button(self):
        self.record_video_button = QtWidgets.QPushButton('Record Video', self)
        self.record_video_button.setCheckable(True)
        self.record_video_button.move(1090, 150)
        self.record_video_button.resize(150, 40)
        self.record_video_button.clicked.connect(self.record_video)

    def create_combobox_selector(self):
        output = [dI for dI in os.listdir('bin/sets') if os.path.isdir(os.path.join('bin/sets', dI))]
        self.combobox_selector = QtWidgets.QComboBox(self)
        self.combobox_selector.move(1090, 50)
        self.combobox_selector.resize(150, 40)
        self.combobox_selector.addItems(output)

    def create_right_image(self):
        self.im_right_label = QtWidgets.QLabel(self)
        self.im_right_label.resize(400, 300)
        self.im_right_label.move(500, 50)
        self.im_right_label.setStyleSheet('background-color: gray')
        self.im_right_label.show()
        self.im_right_txt = QtWidgets.QLabel(self)
        self.im_right_txt.resize(200, 40)
        self.im_right_txt.move(500, 10)
        self.im_right_txt.setText('Image B')
        self.im_right_txt.show()

    def create_left_image(self):
        self.im_left_label = QtWidgets.QLabel(self)
        self.im_left_label.resize(400, 300)
        self.im_left_label.move(50, 50)
        self.im_left_label.setStyleSheet('background-color: gray')
        self.im_left_label.show()
        self.im_left_txt = QtWidgets.QLabel(self)
        self.im_left_txt.resize(200, 40)
        self.im_left_txt.move(50, 10)
        self.im_left_txt.setText('Image A')
        self.im_left_txt.show()

    def create_matching_options_group(self):
        self.matching_options_group = QtWidgets.QGroupBox('Matching Options', self)
        self.matching_options_group.move(50, 375)
        self.vertical_layout = QtWidgets.QVBoxLayout()
        self.vertical_layout.addWidget(QtWidgets.QRadioButton('Radio test'))
        self.vertical_layout.addWidget(QtWidgets.QRadioButton('Radio test2'))
        self.matching_options_group.setLayout(self.vertical_layout)

    def create_options_tabs(self):
        self.options_tabs = QtWidgets.QTabWidget(self)
        self.options_tabs.resize(850, 250)
        self.options_tabs.move(50, 375)
        self.matching_options_widget = QtWidgets.QWidget()
        self.image_preprocessing_options_widget = QtWidgets.QWidget()
        self.options_tabs.addTab(self.matching_options_widget, 'Matching Options')
        self.options_tabs.addTab(self.image_preprocessing_options_widget, 'Pre Options')

        self.matching_options_widget.layout = QtWidgets.QHBoxLayout()

        self.color_spaces_group = QtWidgets.QGroupBox('Color Space')
        self.color_spaces_vertical_layour = QtWidgets.QVBoxLayout()
        self.bgr_color_space_radio_button = QtWidgets.QRadioButton('BGR')
        self.hsv_color_space_radio_button = QtWidgets.QRadioButton('HSV')
        self.grays_color_space_radio_button = QtWidgets.QRadioButton('Grays')
        self.hsv_color_space_radio_button.setChecked(True)
        self.color_spaces_vertical_layour.addWidget(self.bgr_color_space_radio_button)
        self.color_spaces_vertical_layour.addWidget(self.hsv_color_space_radio_button)
        self.color_spaces_vertical_layour.addWidget(self.grays_color_space_radio_button)
        self.color_spaces_group.setLayout(self.color_spaces_vertical_layour)

        self.image_size_group = QtWidgets.QGroupBox('Image Size')
        self.image_size_vertical_layour = QtWidgets.QVBoxLayout()
        self.image_size_1280_720_radio_button = QtWidgets.QRadioButton('1280x720')
        self.image_size_960_540_radio_button = QtWidgets.QRadioButton('960x540')
        self.image_size_640_480_radio_button = QtWidgets.QRadioButton('640x480')
        self.image_size_960_540_radio_button.setChecked(True)
        self.image_size_vertical_layour.addWidget(self.image_size_1280_720_radio_button)
        self.image_size_vertical_layour.addWidget(self.image_size_960_540_radio_button)
        self.image_size_vertical_layour.addWidget(self.image_size_640_480_radio_button)
        self.image_size_group.setLayout(self.image_size_vertical_layour)

        self.epipolar_range_group = QtWidgets.QGroupBox('Ranges')
        self.epipolar_range_vertical_layout = QtWidgets.QVBoxLayout()
        self.epiline_range_combobox_selector = QtWidgets.QComboBox()
        self.epiline_range_combobox_selector.addItems(['Epiline Range', '1', '2', '3', '4', '5'])
        self.patch_size_combobox_selector = QtWidgets.QComboBox()
        self.patch_size_combobox_selector.addItems(['Patch Size', '5', '10', '20', '30', '40'])
        self.epipolar_range_vertical_layout.addWidget(self.epiline_range_combobox_selector)
        self.epipolar_range_vertical_layout.addWidget(self.patch_size_combobox_selector)
        self.epipolar_range_group.setLayout(self.epipolar_range_vertical_layout)

        self.matching_options_widget.layout.addWidget(self.color_spaces_group)
        self.matching_options_widget.layout.addWidget(self.image_size_group)
        self.matching_options_widget.layout.addWidget(self.epipolar_range_group)
        self.matching_options_widget.setLayout(self.matching_options_widget.layout)

    def create_information_tabs(self):
        self.information_tabs = QtWidgets.QTabWidget(self)
        self.information_tabs.resize(300, 250)
        self.information_tabs.move(925, 375)
        self.matching_information_widget = QtWidgets.QWidget()
        self.calibration_information_widget = QtWidgets.QWidget()
        self.information_tabs.addTab(self.matching_information_widget, 'Matching Info')

        self.matching_information_widget.layout = QtWidgets.QVBoxLayout()
        self.matching_information_points_to_match_label = QtWidgets.QLabel('Points to match: %s' % 0)
        self.matching_information_points_matched_label = QtWidgets.QLabel('Points matched: %s' % 0)
        self.matching_information_seconds_per_point_label = QtWidgets.QLabel('Seconds per Point: %s' % 0)
        self.matching_information_total_matching_seconds_label = QtWidgets.QLabel('Matching time (s): %s' % 0)


        self.matching_information_widget.layout.addWidget(self.matching_information_points_to_match_label)
        self.matching_information_widget.layout.addWidget(self.matching_information_points_matched_label)
        self.matching_information_widget.layout.addWidget(self.matching_information_seconds_per_point_label)
        self.matching_information_widget.layout.addWidget(self.matching_information_total_matching_seconds_label)

        self.matching_information_widget.setLayout(self.matching_information_widget.layout)


    def create_main_window(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("Vision")
        self.resize(1250, 650)
        self.move(150, 50)
        self.updGUI.connect(self.update)

    def set_cameras(self, cameras):
        self.cameras = cameras

    def update(self):
        if self.cameras is not None:
            if self.take_calibration_images.isChecked():
                self.frames += 1
                if self.frames == 100:
                    self.take_calibration_image()
                    self.frames = 0

            if self.should_record_video is True:
                self.update_video_recorder()

            im_left = self.cameras[0].getImage()
            if im_left is not None:
                im_left = cv2.cvtColor(im_left, cv2.COLOR_BGR2RGB)
                im = QtGui.QImage(im_left.data, im_left.shape[1], im_left.shape[0],QtGui.QImage.Format_RGB888)
                im_scaled = im.scaled(self.im_left_label.size())
                self.im_left_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled))  # We get the original image and display it.

            im_right = self.cameras[1].getImage()
            if im_right is not None:
                im_right = cv2.cvtColor(im_right, cv2.COLOR_BGR2RGB)
                im = QtGui.QImage(im_right.data, im_right.shape[1], im_right.shape[0],QtGui.QImage.Format_RGB888)
                im_scaled = im.scaled(self.im_left_label.size())
                self.im_right_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled)) # We get the original image and display it.

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
        if not os.path.exists('bin/sets/' + self.combobox_selector.currentText()):
            os.makedirs('bin/sets/' + self.combobox_selector.currentText())

        if not os.path.exists('bin/sets/' + self.combobox_selector.currentText() + '/images'):
            os.makedirs('bin/sets/' + self.combobox_selector.currentText() + '/images')

        self.photos_taken += 1
        print('Take Dual Image ' + str(self.photos_taken))

        print('::Write Left Image::')
        im_left = self.cameras[0].get_image_hd()
        #im_rgb_left = cv2.cvtColor(cv2.resize(im_left,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.combobox_selector.currentText() + '/images/left_image_' + str(self.photos_taken) + '.png',im_left)
        
        print('::Write Right Image::')
        im_right = self.cameras[1].get_image_hd()
        #im_rgb_right = cv2.cvtColor(cv2.resize(im_right,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.combobox_selector.currentText() + '/images/right_image_' + str(self.photos_taken) + '.png',im_right)

        self.images_counter.setNum(self.photos_taken)

    def take_calibration_image(self):
        if not os.path.exists('bin/sets/' + self.combobox_selector.currentText() + '/calibration_images'):
            os.makedirs('bin/sets/' + self.combobox_selector.currentText() + '/calibration_images')

        self.photos_taken += 1
        print('Take Dual Image ' + str(self.photos_taken))

        print('::Write Left Image::')
        im_left = self.cameras[0].get_image_hd()
        #im_rgb_left = cv2.cvtColor(cv2.resize(im_left, (1280, 720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.combobox_selector.currentText() + '/calibration_images/left_image_' + str(self.photos_taken) + '.png',
                    im_left)

        print('::Write Right Image::')
        im_right = self.cameras[1].get_image_hd()
        #im_rgb_right = cv2.cvtColor(cv2.resize(im_right, (1280, 720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/sets/' + self.combobox_selector.currentText() + '/calibration_images/right_image_' + str(self.photos_taken) + '.png',
                    im_right)

        self.images_counter.setNum(self.photos_taken)

    def update_video_recorder(self):
        im_left = self.cameras[0].getImageHD()
        im_rgb_left = cv2.cvtColor(cv2.resize(im_left, (1280, 720)), cv2.COLOR_BGR2RGB)
        self.video_recorder_1.write(im_rgb_left)

        im_right = self.cameras[1].getImageHD()
        im_rgb_right = cv2.cvtColor(cv2.resize(im_right, (1280, 720)), cv2.COLOR_BGR2RGB)
        self.video_recorder_2.write(im_rgb_right)

    def calibrate_set(self):
        stereo_calibrator = StereoCalibrationFromChessboard()
        stereo_calibrator.execute(self.combobox_selector.currentText())

    def reconstruct_from_video(self):
        video_reconstructor = ReconstructionFromVideo(
            'bin/sets/' + self.combobox_selector.currentText() + '/videos/video_1.avi',
            'bin/sets/' + self.combobox_selector.currentText() + '/videos/video_2.avi',
            'bin/sets/' + self.combobox_selector.currentText() + '/calibrated_camera.yml'
        )
        video_reconstructor.run()

    def reconstruct_from_images(self):
        images_reconstructor = ReconstructionFromImages(
            'bin/sets/' + self.combobox_selector.currentText() + '/images/left_image_1.png',
            'bin/sets/' + self.combobox_selector.currentText() + '/images/right_image_1.png',
            'bin/sets/' + self.combobox_selector.currentText() + '/calibrated_camera.yml',
            'bin/sets/' + self.combobox_selector.currentText() + '/camera_A_calibration.yml',
            'bin/sets/' + self.combobox_selector.currentText() + '/camera_B_calibration.yml',
            self
        )
        images_reconstructor.run()

    def create_new_set(self):
        if not os.path.exists('bin/sets/' + self.textbox.text()):
            os.makedirs('bin/sets/' + self.textbox.text())

    def show_cameras(self):
        reconstructor = RecontructCameras('bin/sets/' + self.combobox_selector.currentText() + '/calibrated_camera.yml')
        reconstructor.run()
