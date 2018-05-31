import yaml
import os
import numpy as np
import cv2



if __name__ == '__main__':
    with open("calibrated_camera.yml", 'r') as stream:
        try:
            data = yaml.load(stream) 

            rectify_scale = 0 # 0=full crop, 1=no crop
            R1, R2, P1, P2, Q, roi1, roi2 = cv2.stereoRectify(data["cameraMatrix1"], data["distCoeffs1"], data["cameraMatrix2"], data["distCoeffs2"], (640, 480), data["R"], data["T"], alpha = rectify_scale)

            print roi2
            print R1
            print R2
            print Q


            left_maps = cv2.initUndistortRectifyMap(data["cameraMatrix1"], data["distCoeffs1"], R1, P1, (640, 480), cv2.CV_16SC2)
            right_maps = cv2.initUndistortRectifyMap(data["cameraMatrix2"], data["distCoeffs2"], R2, P2, (640, 480), cv2.CV_16SC2)


            img_left = cv2.imread('left_image_3.png')
            gray_left = cv2.cvtColor(img_left,cv2.COLOR_BGR2GRAY)
            img_right = cv2.imread('right_image_3.png')
            gray_right = cv2.cvtColor(img_right,cv2.COLOR_BGR2GRAY)
             
            left_img_remap = cv2.remap(gray_left, left_maps[0], left_maps[1], cv2.INTER_LANCZOS4)
            right_img_remap = cv2.remap(gray_right, right_maps[0], right_maps[1], cv2.INTER_LANCZOS4)

            print type(gray_right)
            print gray_right.shape
            print gray_right
            print type(right_img_remap)
            print right_img_remap.shape
            print right_img_remap

            cv2.imshow("image 1", left_img_remap)
            cv2.imshow("image 2", right_img_remap)
            cv2.waitKey(0)

        except yaml.YAMLError as exc:
            print(exc)