#
# Created on Mar 7, 2017
#
# @author: dpascualhe
#
# Based on @nuriaoyaga code:
# https://github.com/RoboticsURJC-students/2016-tfg-nuria-oyaga/blob/
#     master/camera/camera.py
#
# And @Javii91 code:
# https://github.com/Javii91/Domotic/blob/master/Others/cameraview.py
#

import sys
import random
import traceback
import threading

import cv2
import numpy as np
import easyiceconfig as EasyIce
from PIL import Image
from jderobot import CameraPrx


class Camera:

    def __init__ (self):
        status = 0
        ic = None
        
        sys.argv.append('config/cameraview_test.cfg')
        print sys.argv
        # Initializing the Ice run-time.
        ic = EasyIce.initialize(sys.argv)

        properties = ic.getProperties()
        print ic
        print properties
        self.lock = threading.Lock()
    
        try:
            # We obtain a proxy for the camera.
            obj = ic.propertyToProxy("3DReconstructor.Camera.Proxy")
            print obj
            # We get the first image and print its description.
            self.cam = CameraPrx.checkedCast(obj)
            if self.cam:
                self.im = self.cam.getImageData("RGB8")
                self.im_height = self.im.description.height
                self.im_width = self.im.description.width
                print(self.im.description)
            else: 
                print("Interface camera not connected")
                    
        except:
            traceback.print_exc()
            exit()
            status = 1

    def getImage(self):
        ''' Gets the image from the webcam and returns the original
        image with a ROI draw over it and the transformed image that
        we're going to use to make the prediction.
        '''  
        print self.cam  
        if self.cam:            
            self.lock.acquire()
            
            im = np.zeros((self.im_height, self.im_width, 3), np.uint8)
            im = np.frombuffer(self.im.pixelData, dtype=np.uint8)
            im.shape = self.im_height, self.im_width, 3
                        
            self.lock.release()
            
            return im
    
    def update(self):
        ''' Updates the camera every time the thread changes. '''
        if self.cam:
            self.lock.acquire()
            
            self.im = self.cam.getImageData("RGB8")
            self.im_height = self.im.description.height
            self.im_width = self.im.description.width
            
            self.lock.release()
        
        