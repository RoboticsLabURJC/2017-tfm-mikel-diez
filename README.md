# Visual perception on an autonomous boat
The scope of this project is use of neural networks in order to estimate depth on fish-eye images to enhance the perception capabilities of an autonomous boat. 

## Table of contents

- [Work Log](#cameracalibration)
  * [Current Week](#current-week)
  * [2018 - 2019](#2018---2019)
  * [2017 - 2018](#2017---2018)

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

## Work Log

### Current Week
#### Week Scope
* [ ] Points matching in an RGB color space
* [ ] Full fish-eye camera calibration
#### Week Log

### 2018 - 2019
#### 22/02/2019 - 1/03/2019
More about epilines, now with more points
![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/multiple_epipolars.png)

With even more points
![Infinite Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/infinite_dots_epipopar.png)


More dense reconstruction (click the image to see the video):

[![Watch the video](https://img.youtube.com/vi/1oKkwc_CYgo/hqdefault.jpg)](https://youtu.be/1oKkwc_CYgo)

#### 11/02/2019 - 21/02/2019
So in the end I managed to paint some pretty neat epilines 
![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/epilines.png)

And could make my first reconstruction... which is a bit disappointing as all the points are in the same plane but the position seems odd.
![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/first3Dreconstruction.png)

#### 05/02/2019 - 11/02/2019
Finally I managed to create a docker environment to work here I show how it looks (click the image to see the video):

[![Watch the video](https://img.youtube.com/vi/7MMtTwaH4tQ/hqdefault.jpg)](https://youtu.be/7MMtTwaH4tQ)

The main features of this are the following:
* I have created a docker image with the jderobot installation and other things I might need using a base of ubuntu 16.04
* I use a docker-compose.yml file to launch the image and set the ports/devices(cameras)/display
* From inside the docker the usb plugged cameras can be accessed
* From inside the docker the application GUI is generated

This is now in a very early stage but seems to be working correctly. I also managed to use GUI with docker on OSX but the cameras access seem to be far more complicated. Once the documentation is ready I'll post it here again with the links.

After a few fixes now I can also run de 3DVizWeb inside docker without problem. See the video bellow.

[![Watch the video](https://img.youtube.com/vi/WW9DM6yfyBY/hqdefault.jpg)](https://youtu.be/WW9DM6yfyBY)

Now lets do a 3D reconstruction.

#### 25/01/2019 - 04/02/2019
I make some major changes in my calibration process to avoid certain mistakes I was having:
![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/calibration_tool.png)

I also started doing some experiments with docker as I some times find my self with a different computer than my own and now I managed to create a working environment that I can move to different machines.

Anyway I'm still working in the 3D reconstruction but now things should go more smoothly.

#### 08/01/2019 - 14/01/2019
So after a few more attempts I managed to use the 3DVizWeb to create a "mash" of points and some segments.

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/3DVizWeb_points_small.png)
![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/3DVizWeb_segments_small.png)

In the end it was easier than it seemed and I had to do the following under the viewerBuffer.py file:
Points:
```python
bufferpoints = [
    jderobot.RGBPoint(), 
    jderobot.RGBPoint(10.0,0.0,0.0), 
    jderobot.RGBPoint(-10.0,0.0,0.0),
    jderobot.RGBPoint(0.0,10.0,0.0),
    jderobot.RGBPoint(0.0,-10.0,0.0), 
    jderobot.RGBPoint(0.0,0.0,10.0),
    jderobot.RGBPoint(0.0,0.0,-10.0)
]
```

Segments:
```python
bufferline = [
    jderobot.RGBSegment(jderobot.Segment(jderobot.Point(10.0,0.0,0.0),jderobot.Point(-10.0,0.0,0.0)), jderobot.Color(0.0,0.0,0.0)),
    jderobot.RGBSegment(jderobot.Segment(jderobot.Point(0.0,10.0,0.0),jderobot.Point(0.0,-10.0,0.0)), jderobot.Color(0.0,0.0,0.0)),
    jderobot.RGBSegment(jderobot.Segment(jderobot.Point(0.0,0.0,10.0),jderobot.Point(0.0,0.0,-10.0)), jderobot.Color(0.0,0.0,0.0))
]
```

##### Fish-eye images
Finally by using double sided tape I managed to transform my pinhole webcams to a fish-eye webcam. In the images bellow you can see how the angle of the fish-eyed camera is wider than the normal pinhole camera. Also the quality of the image as it reaches the edges decreases.

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/pinhole_image.png)
![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/fish_eye_image.png)

I'm having some trouble calibrating this images due the bad quality of the images. I might need to try a different lighting and a different pattern for the calibration (a bigger one).

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/bad_calibration_image.png)


#### Resuming the project
Last year I started with this really interesting project and now I'll start again working on it. I might change a bit how this entry looks en the next days or even switch to Github but we'll see. First lets make a summary of where did I leave everything:
* Build stereo camera system: Done
* Stereo calibration for pinhole cameras: Done
* Stereo calibration for fish-eye cameras: ToDo
* Use of 3DVizWeb to represent the dots: ToDo
* Stereo pixels match (using simple patch comparison): Done

Lot of things to do, yes. The first step in this project is to have a classic 3D reconstruction and after that have a classic 3D reconstruction with fish-eye cameras. Anyway once the calibration of the fish-eye cameras and the rectification is done both problems should be similar to solve.

[![Watch the video](https://img.youtube.com/vi/SFbgUE0KqYc/hqdefault.jpg)](https://youtu.be/SFbgUE0KqYc)

One of the most critical things for me to progress in this project as the 3D reconstruction works is to see if I can show this in a 3D viewer this is the first successful attempt to use it. I'm still researching this but it seems to be changing coordinates every few seconds. I'll take a look. 

Then for fish-eye calibration I run into [this tutorial](https://medium.com/@kennethjiang/calibrate-fisheye-lens-using-opencv-333b05afa0b0) and will be trying to use it to help me achieve my goals.
### 2017 - 2018



