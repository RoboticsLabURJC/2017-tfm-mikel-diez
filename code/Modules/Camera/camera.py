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

    def __init__ (self,cam):
        ''' Camera class gets images from live video. '''

        self.cam = cam
        self.count = 0
        self.lock = threading.Lock()

        if self.cam.hasproxy():
            self.im = self.cam.getImage()
            self.im_height = self.im.height
            self.im_width = self.im.width

            print('Image size: {0}x{1} px'.format(
                self.im_width, self.im_height))
        else:
            raise SystemExit("Interface camera not connected")

    def getImage(self):
        ''' Gets the image from the webcam and returns the original image. '''
        if self.cam:
            im = np.frombuffer(self.im.data, dtype=np.uint8)
            im = self.transformImage(im)
            im = np.reshape(im, (540, 404, 3))
            return im

    def getImageHD(self):
        if self.cam:
            im = np.frombuffer(self.im.data, dtype=np.uint8)
            im = np.reshape(im, (self.im_height, self.im_width, 3))
            return im

    def transformImage(self, im):
        im_resized = np.reshape(im, (self.im_height, self.im_width, 3))
        im_resized = cv2.resize(im_resized, (404, 540))
        return im_resized

    def update(self):
        ''' Updates the camera every time the thread changes. '''
        if self.cam:
            self.lock.acquire()

            self.im = self.cam.getImage()
            self.im_height = self.im.height
            self.im_width = self.im.width

            self.lock.release()
        
        