from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from src.vision.reconstruction.use_cases.reconstruction_from_video import ReconstructionFromVideo
from src.vision.reconstruction.use_cases.reconstruction_from_images import ReconstructionFromImages
from src.vision.calibration.use_cases.stereo_calibration_from_chessboard import StereoCalibrationFromChessboard
from src.vision.reconstruction.use_cases.reconstruction_cameras_from_calibration import RecontructCameras

from src.vision.presentation.user_interface.partials.options import Options
from src.vision.presentation.user_interface.partials.actions import Actions
from src.vision.presentation.user_interface.partials.cameras import Cameras
from src.vision.presentation.value_objects.configuration_value_object import ConfigurationValueObject


import os
import cv2


class Application(QtWidgets.QWidget):
    
    updGUI = QtCore.pyqtSignal()
    photos_taken = 0
    frames = 0

    def __init__(self, parent=None):
        self.configuration = ConfigurationValueObject.build_configuration_from_file('Configuration/application.yml')
        self.cameras = None

        self.create_main_window(parent)

        self.create_set_control_widget()
        self.create_cameras_widget()

        self.actions = Actions(self)
        self.options = Options(self)

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

    def create_combobox_selector(self):
        output = [dI for dI in os.listdir('bin/sets') if os.path.isdir(os.path.join('bin/sets', dI))]
        self.combobox_selector = QtWidgets.QComboBox(self)
        self.combobox_selector.move(1090, 50)
        self.combobox_selector.resize(150, 40)
        self.combobox_selector.addItems(output)
        self.combobox_selector.activated.connect(self.set_sets_folder_name)
        self.combobox_selector.setCurrentIndex(0)

    def set_sets_folder_name(self, item):
        self.actions.calibration_information.set_current_folder(self.combobox_selector.itemText(item))

    def update_combo_selector(self, new_item):
        sets = [dI for dI in os.listdir('bin/sets') if os.path.isdir(os.path.join('bin/sets', dI))]
        index = self.combobox_selector.findText(new_item, QtCore.Qt.MatchFixedString)
        self.combobox_selector.clear()
        self.combobox_selector.addItems(sets)
        if index >= 0:
            self.combobox_selector.setCurrentIndex(index)

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

    def create_main_window(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("Vision")
        self.resize(1250, 650)
        self.move(150, 50)
        self.updGUI.connect(self.update)

    def create_set_control_widget(self):
        self.create_input_textbox()
        self.create_new_folder_button()
        self.create_combobox_selector()

    def create_cameras_widget(self):
        self.create_left_image()
        self.create_right_image()

        self.video_recorder_1 = None
        self.video_recorder_2 = None
        self.should_record_video = False

        self.video_capture1 = cv2.VideoCapture(1)
        self.video_capture2 = cv2.VideoCapture(2)

    def set_cameras(self, cameras):
        self.cameras = cameras

    def update(self):
        if self.cameras is not None:
            if self.actions.should_take_calibration_images():
                self.actions.take_calibration_image()
            elif self.should_record_video is True:
                self.update_video_recorder()

            self.update_gui_cameras()

    def update_gui_cameras(self):
        im_left = self.cameras[0].getImage()
        if im_left is not None:
            im_left = cv2.cvtColor(im_left, cv2.COLOR_BGR2RGB)
            im = QtGui.QImage(im_left.data, im_left.shape[1], im_left.shape[0], QtGui.QImage.Format_RGB888)
            im_scaled = im.scaled(self.im_left_label.size())
            self.im_left_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled))
        im_right = self.cameras[1].getImage()
        if im_right is not None:
            im_right = cv2.cvtColor(im_right, cv2.COLOR_BGR2RGB)
            im = QtGui.QImage(im_right.data, im_right.shape[1], im_right.shape[0], QtGui.QImage.Format_RGB888)
            im_scaled = im.scaled(self.im_left_label.size())
            self.im_right_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled))

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

    def update_video_recorder(self):
        im_left = self.cameras[0].getImageHD()
        im_rgb_left = cv2.cvtColor(cv2.resize(im_left, (1280, 720)), cv2.COLOR_BGR2RGB)
        self.video_recorder_1.write(im_rgb_left)

        im_right = self.cameras[1].getImageHD()
        im_rgb_right = cv2.cvtColor(cv2.resize(im_right, (1280, 720)), cv2.COLOR_BGR2RGB)
        self.video_recorder_2.write(im_rgb_right)

    def create_new_set(self):
        if not os.path.exists('bin/sets/' + self.textbox.text()):
            os.makedirs('bin/sets/' + self.textbox.text())
            self.update_combo_selector(self.textbox.text())
