import numpy as np
import cv2
import glob
import yaml

if __name__ == '__main__':
    #Stop criteria
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # Pattern Size
    pattern_size = (8,6)

    # Images format
    images_format = '.png'


    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((pattern_size[1]*pattern_size[0],3), np.float32)
    objp[:,:2] = np.mgrid[0:pattern_size[0],0:pattern_size[1]].T.reshape(-1,2)  

    # Arrays to store object points and image points from all the images.
    objpoints = [] # 3d point in real world space
    imgpoints_left = [] # 2d points in image plane.
    imgpoints_right = [] # 2d points in image plane.
    image_size = []

    images_left = sorted(glob.glob('bin/CalibrationImages/set_fish/left*' + images_format))
    images_right = sorted(glob.glob('bin/CalibrationImages/set_fish/right*' + images_format))

    print images_left
    print images_right


    for index,fname in enumerate(images_left):

        # Load images and convert to gray
        img_left = cv2.imread(fname)
        gray_left = cv2.cvtColor(img_left,cv2.COLOR_BGR2GRAY)
        img_right = cv2.imread(images_right[index])
        gray_right = cv2.cvtColor(img_right,cv2.COLOR_BGR2GRAY)

        image_size = img_left.shape

        # Find the chess board corners in both images
        left_found, left_corners = cv2.findChessboardCorners(gray_left, pattern_size,cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)
        right_found, right_corners = cv2.findChessboardCorners(gray_right, pattern_size,cv2.CALIB_CB_ADAPTIVE_THRESH | cv2.CALIB_CB_NORMALIZE_IMAGE | cv2.CALIB_CB_FAST_CHECK)

        if left_found:
            cv2.cornerSubPix(gray_left,left_corners,(11,11),(-1,-1),criteria)
        if right_found:
            cv2.cornerSubPix(gray_right,right_corners,(11,11),(-1,-1),criteria) 


        # If found, add object points, image points (after refining them)
        if left_found and right_found:
            objpoints.append(objp)
            imgpoints_left.append(left_corners)
            imgpoints_right.append(right_corners)

        # Draw and display the corners
        cv2.drawChessboardCorners(img_left, pattern_size, left_corners,left_found)
        cv2.drawChessboardCorners(img_right, pattern_size, right_corners,right_found)
        cv2.imshow('Left Image',img_left)
        cv2.waitKey(500)

    # Destroy windows
    cv2.destroyAllWindows()


    # Calibrate cameras individualy
    ret1, cameraMatrix1, distCoeffs1, rvecs1, tvecs1 = cv2.fisheye.calibrate(objpoints, imgpoints_left, gray_left.shape[::-1],None,None)
    ret2, cameraMatrix2, distCoeffs2, rvecs2, tvecs2 = cv2.fisheye.calibrate(objpoints, imgpoints_right, gray_right.shape[::-1],None,None)


    # print cameraMatrix1 
    # print distCoeffs1
    # print cameraMatrix2 
    # print distCoeffs2

    # print 'objpoints'
    # print objpoints
    # print 'imgpoints_left'
    # print imgpoints_left
    # print 'imgpoints_right'
    # print imgpoints_right

    # Calibrate stereo camera
    stereocalib_criteria = (cv2.TERM_CRITERIA_MAX_ITER + cv2.TERM_CRITERIA_EPS, 100, 1e-5)
    # stereocalib_flags = cv2.CALIB_FIX_ASPECT_RATIO | cv2.CALIB_ZERO_TANGENT_DIST | cv2.CALIB_SAME_FOCAL_LENGTH | cv2.CALIB_RATIONAL_MODEL | cv2.CALIB_FIX_K3 | cv2.CALIB_FIX_K4 | cv2.CALIB_FIX_K5

    stereocalib_flags = cv2.CALIB_FIX_INTRINSIC
    stereocalib_retval, cameraMatrix1, distCoeffs1, cameraMatrix2, distCoeffs2, R, T, E, F = cv2.stereoCalibrate(objpoints,imgpoints_left,imgpoints_right,cameraMatrix1,distCoeffs1,cameraMatrix2,distCoeffs2,gray_left.shape[::-1],criteria = stereocalib_criteria, flags = stereocalib_flags)


   
    
    # Save the calibration matrix in a yaml file.
    with open('bin/CalibrationMatrix/calibrated_camera.yml', 'w') as outfile:
        yaml.dump({'stereocalib_retval': stereocalib_retval, 'cameraMatrix1': cameraMatrix1, 'distCoeffs1': distCoeffs1,'cameraMatrix2': cameraMatrix2, 'distCoeffs2': distCoeffs2, 'R': R,'T':T, 'E': E, 'F': F}, outfile, default_flow_style=False)

    # Check the error of the meassure
    tot_error = 0
    for i in xrange(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs1[i], tvecs1[i], cameraMatrix1, distCoeffs1)
        error = cv2.norm(imgpoints_left[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        tot_error += error 
    print "total error left: ", tot_error/len(objpoints)
    for i in xrange(len(objpoints)):
        imgpoints2, _ = cv2.projectPoints(objpoints[i], rvecs2[i], tvecs2[i], cameraMatrix2, distCoeffs2)
        error = cv2.norm(imgpoints_right[i],imgpoints2, cv2.NORM_L2)/len(imgpoints2)
        tot_error += error 
    print "total error right: ", tot_error/len(objpoints)
    print 'ret1; ', ret1
    print 'ret2: ', ret2
    print 'retval: ', stereocalib_retval
