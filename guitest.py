import sys
import signal


from PyQt5 import QtWidgets

from Application.application import Application
from Application.threadapplication import ThreadApplication
from Camera.camera import Camera
from Camera.threadcamera import ThreadCamera

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    # For the widget we need to create an application object
    application = QtWidgets.QApplication(sys.argv)

    camera = Camera()
    myGUI = Application()
    myGUI.setCameras(camera)
    myGUI.show()

    # Threading camera
    t_cam = ThreadCamera(camera)
    t_cam.daemon = True
    t_cam.start()

    t_gui = ThreadApplication(myGUI)
    t_gui.daemon = True
    t_gui.start()

    # When user closes the Widget
    sys.exit(application.exec_())
