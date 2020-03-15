import sys
import signal


from PyQt5 import QtWidgets

from src.vision.presentation.user_interface.application import Application
from src.vision.presentation.user_interface.threadapplication import ThreadApplication
from src.vision.presentation.value_objects.camera import Camera
from src.vision.presentation.value_objects.openCvCamera import openCvCamera
from src.vision.presentation.value_objects.threadcamera import ThreadCamera

import config
import comm

signal.signal(signal.SIGINT, signal.SIG_DFL)

if __name__ == '__main__':
    # For the widget we need to create an application object
    application = QtWidgets.QApplication(sys.argv)

    print(sys.path)
    # TEST YML
    right_camera_config = config.load('Configuration/cameraview_right.yml')
    left_camera_config = config.load('Configuration/cameraview_left.yml')

    try:
        # jdrc = comm.init(right_camera_config, 'Cameraview')
        # proxy = jdrc.getCameraClient('Cameraview.Camera')
        # camera_right = Camera(proxy)
        camera_right = openCvCamera(2)

        # jdrc = comm.init(left_camera_config, 'Cameraview')
        # proxy = jdrc.getCameraClient('Cameraview.Camera')
        # camera_left = Camera(proxy)
        camera_left = openCvCamera(4)

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
