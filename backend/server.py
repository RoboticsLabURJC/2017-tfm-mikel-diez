#!/usr/bin/env python
from flask import Flask, render_template, Response
import cv2
import json
import os

from src.vision.calibration.use_case.CalibrateStereoCamerasFromChessboard import CalibrateStereoCamerasFromChessboard
from src.vision.reconstruction.use_case.reconstruction_cameras_from_calibration import RecontructCameras

import logging

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

camera_capture = None


def get_frame():
    global camera_capture
    while True:
        retval, im = camera_capture.read()
        imgencode = cv2.imencode('.jpg', im)[1]
        stringData = imgencode.tostring()
        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

    del(camera_capture)


@app.route('/camera/<int:camera_port>')
def camera(camera_port):
    global camera_capture
    camera_capture = cv2.VideoCapture(camera_port)
    return Response(get_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/takeimage/<string:images_set>')
def take_image(images_set):
    global camera_capture
    retval, image = camera_capture.read()
    cv2.imwrite('hola.png', image)
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/calibrate/<string:images_set>')
def calibrate(images_set):
    calibrate_stereo_cameras_from_chessboad = CalibrateStereoCamerasFromChessboard()
    backproject_error = calibrate_stereo_cameras_from_chessboad.execute(images_set)

    return json.dumps({'data': backproject_error}), 200, {'ContentType': 'application/json'}


@app.route('/showcameras/<string:images_set>')
def show_cameras(images_set):
    calibration_file = 'bin/sets/' + 'set_canonical' + '/calibrated_camera.yml'
    app.logger.info('%s logged in successfully', calibration_file)
    reconstruct_cameras = RecontructCameras(calibration_file)
    app.logger.info('Reconstructior Created')
    reconstruct_cameras.execute()
    app.logger.info('Reconstructor Executed')
    return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}


@app.route('/sets')
def sets():
    output = [dI for dI in os.listdir('bin/sets') if os.path.isdir(os.path.join('bin/sets', dI))]
    return json.dumps({'data': output}), 200, {'ContentType': 'application/json'}


@app.route('/reconstruct_image/<string:images_set>')
def reconstruct_image(images_set):
    return json.dumps({'data': True}), 200, {'ContentType': 'application/json'}


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)
