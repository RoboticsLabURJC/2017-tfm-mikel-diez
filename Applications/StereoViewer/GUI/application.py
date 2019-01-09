import sys

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

import cv2

class Application(QtWidgets.QWidget):
    
    updGUI = QtCore.pyqtSignal()
    photos_taken = 0
    frames = 0

    def __init__(self,parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("3D Reconstruction")
        self.resize(1100, 600)
        self.move(150, 50)

        self.updGUI.connect(self.update)

        # Original image label.
        self.im_left_label = QtWidgets.QLabel(self)
        self.im_left_label.resize(400, 300)
        self.im_left_label.move(50, 50)
        self.im_left_label.show()
        self.im_left_txt = QtWidgets.QLabel(self)
        self.im_left_txt.resize(200, 40)
        self.im_left_txt.move(50, 10)
        self.im_left_txt.setText('Left Image')
        self.im_left_txt.show()

        # Original image label.
        self.im_right_label = QtWidgets.QLabel(self)
        self.im_right_label.resize(400, 300)
        self.im_right_label.move(500, 50)
        self.im_right_label.show()
        self.im_right_txt = QtWidgets.QLabel(self)
        self.im_right_txt.resize(200, 40)
        self.im_right_txt.move(500, 10)
        self.im_right_txt.setText('Right Image')
        self.im_right_txt.show()

        # Button to take a shot of both cameras one time and store it
        self.take_photo_button = QtWidgets.QPushButton('Take Photo', self)
        self.take_photo_button.move(950, 50)
        self.take_photo_button.clicked.connect(self.takePhoto)

        # Button to take a shot of both cameras one time and store it
        self.take_calibration_images = QtWidgets.QPushButton('Calibration Images', self)
        self.take_calibration_images.setCheckable(True)
        self.take_calibration_images.move(950, 100)
        self.take_calibration_images.clicked.connect(self.takePhoto)

        self.toolbar=QtWidgets.QToolBar()
        self.toolbar.setIconSize(QtCore.QSize(48, 48))

        self.tb_save = QtWidgets.QAction(QtGui.QIcon("../test/icon.png"), "Save graph", self)
        self.tb_save.triggered.connect(self.takePhoto)
        self.toolbar.addAction(self.tb_save)


    def setCameras  (self,cameras):
        self.cameras = cameras

    def update(self):
        if(self.take_calibration_images.isChecked()):
            self.frames += 1
            if(self.frames == 100):
                self.takePhoto()
                self.frames = 0

        im_left = self.cameras[0].getImage()
        im = QtGui.QImage(im_left.data, im_left.shape[1], im_left.shape[0],QtGui.QImage.Format_RGB888)
        im_scaled = im.scaled(self.im_left_label.size())
        self.im_left_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled)) # We get the original image and display it.

        im_right = self.cameras[1].getImage()
        im = QtGui.QImage(im_right.data, im_right.shape[1], im_right.shape[0],QtGui.QImage.Format_RGB888)
        im_scaled = im.scaled(self.im_left_label.size())
        self.im_right_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled)) # We get the original image and display it.

    def takePhoto(self):
        self.photos_taken += 1
        print 'Take Dual Image ' + str(self.photos_taken)

        print '::Write Left Image::'
        im_left = self.cameras[0].getImage()
        im_rgb_left = cv2.cvtColor(cv2.resize(im_left,(640,480)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/CalibrationImages/left_image_' + str(self.photos_taken) + '.png',im_rgb_left)
        
        print '::Write Right Image::'
        im_right = self.cameras[1].getImage()
        im_rgb_right = cv2.cvtColor(cv2.resize(im_right,(640,480)), cv2.COLOR_BGR2RGB)
        cv2.imwrite('bin/CalibrationImages/right_image_' + str(self.photos_taken) + '.png',im_rgb_right)

