from PyQt5 import QtWidgets

class Cameras(QtWidgets.QTabWidget):

    def __init__(self, cameras, parent=None):
        super(QtWidgets.QTabWidget, self).__init__(parent)
        self.cameras = cameras
        self.parent = parent
