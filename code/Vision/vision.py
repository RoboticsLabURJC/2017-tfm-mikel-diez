import sys
import signal


from PyQt5 import QtWidgets

from Vision.GUI.application import Application
from Vision.GUI.threadapplication import ThreadApplication
from Vision.Components.Camera.camera import Camera
from Vision.Components.Camera.openCvCamera import openCvCamera
from Vision.Components.Camera.threadcamera import ThreadCamera

import config
import comm

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    # For the widget we need to create an application object
    application = QtWidgets.QApplication(sys.argv)


    # TEST YML
    right_camera_config = config.load('Configuration/cameraview_right.yml')
    left_camera_config = config.load('Configuration/cameraview_left.yml')

    try:
        # jdrc = comm.init(right_camera_config, 'Cameraview')
        # proxy = jdrc.getCameraClient('Cameraview.Camera')
        # camera_right = Camera(proxy)
        camera_right = openCvCamera(0)

        # jdrc = comm.init(left_camera_config, 'Cameraview')
        # proxy = jdrc.getCameraClient('Cameraview.Camera')
        # camera_left = Camera(proxy)
        camera_left = openCvCamera(2)

        # Cameras configuration
        myGUI = Application()
        myGUI.set_cameras([camera_left, camera_right])
        myGUI.show()

        # Threading camera left
        thread_camera_left = ThreadCamera(camera_left)
        thread_camera_left.daemon = True
        thread_camera_left.start()

        # Threading camera right
        thread_camera_right = ThreadCamera(camera_right)
        thread_camera_right.daemon = True
        thread_camera_right.start()

    except:
        print('No cameras available')
        myGUI = Application()
        myGUI.show()

    t_gui = ThreadApplication(myGUI)
    t_gui.daemon = True
    t_gui.start()

    # When user closes the Widget
    sys.exit(application.exec_())
