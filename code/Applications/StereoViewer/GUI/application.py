import sys

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

from Modules.Calibration.StereoCalibration import StereoCalibration
from Modules.Matching.imagematcher import BorderStereoMatcher

import os
import yaml
import cv2

class Application(QtWidgets.QWidget):
    
    updGUI = QtCore.pyqtSignal()
    photos_taken = 0
    frames = 0

    def __init__(self, parent=None):
        print(sys.path)
        self.create_main_window(parent)

        self.create_left_image()
        self.create_right_image()
        self.create_take_photo_button()
        self.create_calibration_images_button()
        self.create_calibrate_cameras_button()
        self.create_reconstruction_button()
        self.create_input_textbox()
        self.create_image_counter_text()

    def create_image_counter_text(self):
        self.images_counter = QtWidgets.QLabel(self)
        self.images_counter.resize(150, 40)
        self.images_counter.move(950, 300)
        self.images_counter.setAlignment(QtCore.Qt.AlignCenter)
        self.images_counter.setFont(QtGui.QFont('Arial', 35))
        self.images_counter.setNum(0)
        self.images_counter.show()

    def create_input_textbox(self):
        self.textbox = QtWidgets.QLineEdit(self)
        self.textbox.move(950, 50)
        self.textbox.resize(150, 40)

    def create_reconstruction_button(self):
        self.reconstruction_button = QtWidgets.QPushButton('3D Reconstruction', self)
        self.reconstruction_button.move(950, 250)
        self.reconstruction_button.resize(150, 40)
        self.reconstruction_button.clicked.connect(self.reconstruct_with_set)

    def create_calibrate_cameras_button(self):
        self.calibrate_button = QtWidgets.QPushButton('Calibrate Cameras', self)
        self.calibrate_button.move(950, 200)
        self.calibrate_button.resize(150, 40)
        self.calibrate_button.clicked.connect(self.calibrate_set)

    def create_calibration_images_button(self):
        self.take_calibration_images = QtWidgets.QPushButton('Calibration Images', self)
        self.take_calibration_images.setCheckable(True)
        self.take_calibration_images.move(950, 150)
        self.take_calibration_images.resize(150, 40)
        self.take_calibration_images.clicked.connect(self.take_photo)

    def create_take_photo_button(self):
        self.take_photo_button = QtWidgets.QPushButton('Take Photo', self)
        self.take_photo_button.move(950, 100)
        self.take_photo_button.resize(150, 40)
        self.take_photo_button.clicked.connect(self.take_photo)

    def create_right_image(self):
        self.im_right_label = QtWidgets.QLabel(self)
        self.im_right_label.resize(400, 300)
        self.im_right_label.move(500, 50)
        self.im_right_label.show()
        self.im_right_txt = QtWidgets.QLabel(self)
        self.im_right_txt.resize(200, 40)
        self.im_right_txt.move(500, 10)
        self.im_right_txt.setText('Right Image')
        self.im_right_txt.show()

    def create_left_image(self):
        self.im_left_label = QtWidgets.QLabel(self)
        self.im_left_label.resize(400, 300)
        self.im_left_label.move(50, 50)
        self.im_left_label.show()
        self.im_left_txt = QtWidgets.QLabel(self)
        self.im_left_txt.resize(200, 40)
        self.im_left_txt.move(50, 10)
        self.im_left_txt.setText('Left Image')
        self.im_left_txt.show()

    def create_main_window(self, parent):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("3D Reconstruction")
        self.resize(1150, 400)
        self.move(150, 50)
        self.updGUI.connect(self.update)

    def set_cameras(self, cameras):
        self.cameras = cameras

    def update(self):
        if(self.take_calibration_images.isChecked()):
            self.frames += 1
            if(self.frames == 100):
                self.take_photo()
                self.frames = 0

        im_left = self.cameras[0].getImage()
        im = QtGui.QImage(im_left.data, im_left.shape[1], im_left.shape[0],QtGui.QImage.Format_RGB888)
        im_scaled = im.scaled(self.im_left_label.size())
        self.im_left_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled)) # We get the original image and display it.

        im_right = self.cameras[1].getImage()
        im = QtGui.QImage(im_right.data, im_right.shape[1], im_right.shape[0],QtGui.QImage.Format_RGB888)
        im_scaled = im.scaled(self.im_left_label.size())
        self.im_right_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled)) # We get the original image and display it.

    def take_photo(self):
        if not os.path.exists('bin/CalibrationImages/' + self.textbox.text()):
            os.makedirs('bin/CalibrationImages/' + self.textbox.text())

        self.photos_taken += 1
        print('Take Dual Image ' + str(self.photos_taken))

        print('::Write Left Image::')
        im_left = self.cameras[0].getImageHD()
        im_rgb_left = cv2.cvtColor(cv2.resize(im_left,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/CalibrationImages/' + self.textbox.text() + '/left_image_' + str(self.photos_taken) + '.png',im_rgb_left)
        
        print('::Write Right Image::')
        im_right = self.cameras[1].getImageHD()
        im_rgb_right = cv2.cvtColor(cv2.resize(im_right,(1280,720)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/CalibrationImages/' + self.textbox.text() + '/right_image_' + str(self.photos_taken) + '.png',im_rgb_right)

        self.images_counter.setNum(self.photos_taken)

    def calibrate_set(self):
        stereo_calibrator = StereoCalibration()
        stereo_calibrator.calibrate_set(self.textbox.text())

    def reconstruct_with_set(self):
        image1 = cv2.imread('bin/CalibrationImages/set12_objectReconstruction/left_image_16.png')
        image2 = cv2.imread('bin/CalibrationImages/set12_objectReconstruction/right_image_16.png')
        matcher = BorderStereoMatcher()
        matcher.set_images(image1, image2)
        with open("bin/CalibrationMatrix/set12/calibrated_camera.yml", 'r') as stream:
            try:
                data = yaml.load(stream)
                matcher.set_calibration_data(data)
            except yaml.YAMLError as exc:
                print(exc)

        matcher.get_matching_points()
