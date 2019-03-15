# Visual perception on an autonomous boat
The scope of this project is use of neural networks in order to estimate depth on fish-eye images to enhance the perception capabilities of an autonomous boat. 

## Table of contents

- [CameraCalibration](#cameracalibration)

<a name="vision"></a>
## StereoViewer
This application lets you use two cameras and take photos with them. I also incorporates a feature to take several images in a row to take the calibration images for the next steps of the project.

### How to use it
Navigate to the folder of the project and execute:
`cameraserver Configuration/cameraserver.cfg`

With that you'll have the server runing with two cameras (keep in mind that if you are using a laptop the video0 could be the built in camera).

Then run:
`python Applications/StereoViewer/stereoviewer.py`

<a name="camera-calibration"></a>
## CameraCalibration
Right now this takes the images from a folder and calibrates both cameras individually and then together (pinhole cameras). To use it just run:
`python Applications/CameraCalibration/calibratecameras.py`

Here is where I'm working right now to add fish-eye lenses calibration.



