# Stereoscopic estimation using DeepLearning
This project is still under development. But in case someone wants to use some of the "applications" I'm working on here is how you can do it. (I'm going to assume you have jderobot already installed and working).

## StereoViewer
This application lets you use two cameras and take photos with them. I also incorporates a feature to take several images in a row to take the calibration images for the next steps of the project.

### How to use it
Navigate to the folder of the project and execute:
`cameraserver Configuration/cameraserver.cfg`

With that you'll have the server runing with two cameras (keep in mind that if you are using a laptop the video0 could be the built in camera).

Then run:
`python Applications/StereoViewer/stereoviewer.py`

## CameraCalibration
Right now this takes the images from a folder and calibrates both cameras individually and then together (pinhole cameras). To use it just run:
`python Applications/CameraCalibration/calibratecameras.py`

Here is where I'm working right now to add fish-eye lenses calibration.

## Other staff
There are other staff that can be used but is incompleted so it does not worth writing it here.
