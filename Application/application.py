import sys

from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

class Application(QtWidgets.QWidget):
    
    updGUI = QtCore.pyqtSignal()

    def __init__(self,parent = None):
        QtWidgets.QWidget.__init__(self, parent)
        self.setWindowTitle("3D Reconstruction")
        self.resize(1000, 600)
        self.move(150, 50)

        self.updGUI.connect(self.update)

        # Original image label.
        self.im_label = QtWidgets.QLabel(self)
        self.im_label.resize(400, 300)
        self.im_label.move(70, 50)
        self.im_label.show()

        # Transformed image label.
        self.im_trans_label = QtWidgets.QLabel(self)
        self.im_trans_label.resize(200, 200)
        self.im_trans_label.move(700, 50)
        self.im_trans_label.show()


    def setCameras  (self,cameras):
        self.cameras = cameras

    def update(self):
        im_prev = self.cameras.getImage()
        im = QtGui.QImage(im_prev.data, im_prev.shape[1], im_prev.shape[0],QtGui.QImage.Format_RGB888)
        im_scaled = im.scaled(self.im_label.size())
        self.im_label.setPixmap(QtGui.QPixmap.fromImage(im_scaled)) # We get the original image and display it.