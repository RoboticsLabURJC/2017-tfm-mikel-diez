# Visual perception on an autonomous boat
The scope of this project is use of neural networks in order to estimate depth on fish-eye images to enhance the perception capabilities of an autonomous boat. 

## Table of contents

- [Work Log](#work-log)
  * [Current Week](#current-week)
  * [2018 - 2019](#2018---2019)
  * [2017 - 2018](#2017---2018)

## Work Log
#### Current Week
##### Week Scope
* [ ] Improve matching with different measures
* [x] Improve and understand better the triangulatepoints function
* [ ] Full fish-eye camera calibration

###### Getting to know cv2.triangulatePoints
In order to recreate the 3D scene I'm trying to use the OpenCV function cv2.triangulatePoints which in python has the following definition:
```python
points4D = cv2.triangulatePoints(projMatr1, projMatr2, projPoints1, projPoints2[, points4D])
```
The points are the ones that the matching algorithm gives me back and the projection matrix are obtained with the use of cv2.stereoRectify
```python
r1, r2, p1, p2, q, roi1, roi2 = cv2.stereoRectify(
			self.calibration_data["cameraMatrix1"],
			self.calibration_data["distCoeffs1"],
			self.calibration_data["cameraMatrix2"],
			self.calibration_data["distCoeffs2"],
			(1280, 720),
			self.calibration_data["R"],
			self.calibration_data["T"],
			alpha=rectify_scale
)
```

Something seems to be out of place and I'm still investigating it.

I've been reading that cv2.triangulatePoints takes as points undistorted points, so I'm checking that out.

So finally I've managed to get what seems to be a better reconstruction, there are still points in a wrong position BUT they are yellow and yellow points seem to be matching in a wrong way. (See video):
[![Watch the video](https://img.youtube.com/vi/zOlYptgbFQ8/hqdefault.jpg)](https://youtu.be/zOlYptgbFQ8)

[Link to OpenCV documentation](https://docs.opencv.org/2.4.13/modules/calib3d/doc/camera_calibration_and_3d_reconstruction.html#triangulatepoints)



##### Week Log
ToDo

### 2018 - 2019
#### 01/03/2019 - 22/03/2019
##### Week Scope
* [x] Points matching in an RGB color space
* [ ] Full fish-eye camera calibration
##### Week Log
As agreed I started working in a tool to see how the points in both images are matched. Unsurprisingly all the lines follow the same direction as they are all following the epiline and they all go in the same direction.

Matching with gray images and MSE threshold of 80

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_threshold_80.png)

Matching with gray images and MSE threshold of 50

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_threshold_50.png)

Matching with rgb images and MSE threshold of 50

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_rgb_threshold_50.png)

Matching with rgb images and MSE threshold of 50 with an epiline range of +-4 pixels.

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_rgb_threshold_50_epilines_4.png)

Matching with hsv color space taking all the channels and without considering the circularity of H

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_hsv_all_channels.png)

Matching with hsv color space taking only H and S with threshold of 50

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_hsv_hs_threshold_50.png)

Matching with hsv color space taking only H and S with threshold of 25

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/matching_hsv_hs_threshold_25.png)

As can be seen in the mos of the miss-matches happen in the lower line of yellow books. I might need to try go get a more texturized images where de difference between interest points is higher. 

Result of a reconstruction (video):

[![Watch the video](https://img.youtube.com/vi/0YSDw8JzDuk/hqdefault.jpg)](https://youtu.be/0YSDw8JzDuk)

With this matches:

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/images/Match_Points_screenshot_21.03.2019.png)

As can be seen it seems that the yellow points tend to be wrongly matched, hence the reconstruction fails. The rest of the points seem to have a more interesting position but still seems to be wrong.

What am I doing right now?
* First find the pixel in both images (similar pixel color tend to make it fail)
* Use the function ```cv2.triangulatePoints``` to calculate the 3D points
* Convert the points returned by the function from quaternions to cartesian coordinates (x/w, y/w, z/w)
* Save the reconstruction with the color
* Show this using 3DWebViz

#### 22/02/2019 - 01/03/2019
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
#### Week 6
I finally managed to create a stereo calibration. As said in previous logs I used the example of the OpenCV documentation to calibrate the single cameras, but then I needed to have the stereo pair and its relative calibration.

Again OpenCV really helps with the process and has a function stereoCalibrate that pretty much do the job for you, you only need to pass the correct parameters to it and now everything is ready to rectify the images.

![Multiple Epilines](https://roboticsurjc-students.github.io/2017-tfm-mikel-diez/rectified_images_screenshot_01.06.2018.png)
#### Between Weeks
I've been like for a month without working much on the thesis (I really regret it), but now I'm back on business. I'm going to write here on the go as the new updates happen instead of waiting until the end to write everything. This way I'll be more engaged with all this (thesis and wiki and github).

Well, first update. I finally got David Pascual's digitclasifier to work! Yes after several problems I got it to work with the new JdeRobot packages.
[![Watch the video](https://img.youtube.com/vi/GjbUXDXEv_o/hqdefault.jpg)](https://youtu.be/GjbUXDXEv_o)

With this new JdeRobot packages the only problem I encounter was that I didn't have the h5py package installed (is listed at [https://keras.io/#installation|Keras] installation documentation as an optional package) but then everything went smoothly.

#### Week 5 (19/12/2017 - 26/12/2017): Lets begin to prepare my solution 
So, this thesis is going to be about depth estimation in stereo images using Deep Learning (likely using convolutional neural networks) but at least in a first attempt CNN will be used to match the corresponding pixels in both images. 

Lets divide the 3D reconstruction from stereo images of a scene in different steps(some of the could contain other sub-steps, but from now we'll go with this):
* Images acquisition
* Pixel matching
* Distance estimation
*3D image reconstruction

The step that will be using CNN is the second. To do this, first a classic geometric solution for stereoscopic 3D reconstruction will be implemented to create a non-dense image of the scene. In the following subsections I'll explain how this first solution is going to be implemented. 

##### Images acquisition
By using the JdeRobot cameraserver I'll connect two cameras to a computer that will process the images. But in a very early stage I'll test the algorithm with a still image (just a photograph) so I'll be able to take it without worrying about other connectivity to test the solution. The rest will come in a later stage when real-time video processing will be necessary.

An other critical part in the acquisition hardware is its calibration, we need to know its intrinsic and extrinsic parameters. The intrinsic parameters are specific to a camera, and once calculated they won't (likely) change, on the other hand, extrinsic parameters are the ones telling the camera position in the real world (rotation, position, tilt).

For this task (calibration) I'll be using OpenCV calibration function ([here a tutorial](https://docs.opencv.org/3.1.0/dc/dbb/tutorial_py_calibration.html)) and I'll need some kind of chess-board pattern. The one in the image is a home-made one.

![Multiple Epilines](http://jderobot.org/store/mikeld/uploads/images/chess_board.jpg)

##### Pixel Matching
In the future this stage will include the CNN but for now I'll proceed with a more classic approach. The objective (at first) is to create a sparse reconstruction, so I'll take only border/corner pixels. Why is that? Well, pixels with high gradient (corners,borders,rough textures) contain much more information than plain surfaces.

For this I'll apply a sobel filter to both images to get the high gradient. Then I'll start taking points in the left image and trying to find them in the right one. But I'll use some restrictions:
*Not all the pixels will be taken only the strongest in the neighbourhood
*I'll use the epipolar restriction, so will only search for coincidences in a bunch or lines over on bellow the original one.
*The pixel on the right image will always be more to the right than in the left image, so there is no use on searching it in the first pixels.
*I'll take the most similar patch except if the similarity is to low or there are several high similarity patches.

And for the similarity measure I'm thinking in a minimum mean square error as it's a basic similarity operator.

##### Distance estimation
Once the pixels have been matched is when the distance estimation begins. By knowing the calibration parameters and the pixels of interest this becomes a geometry problem.

With two points (pixel and camera origin) we can get a line and with two lines we can find an intersection (or the point where they are the closest) and that's the point we are looking for. That's our reconstructed 3D point. I'll extend this in future updates, as this is something I'm going to implement for sure.

##### 3D image reconstruction
Once a list of 3D points is found it's time to show them on the screen. We might use them in many ways but for now lets stick to the previous parts as they are still the main parts of this.

#### Week 4 (11/12/2017 - 18/12/2017): Reproduce code with JdeRobot 
I was having some problem with my python packages version so I decided that it was better to start with a fresh Ubuntu 16.04 installation. I found that ROS had updated some packages and the dependencies where broken so I tried to install it from source code following the [Installation#From_source_code_at_GitHub|installation instructions] from this official source. I didn't have much luck doing this.

There are other staff I had to do for this Mondays meeting:
* Read the thesis of two former students of the course.
  * [Marcos Pieras](https://gsyc.urjc.es/jmplaza/students/tfm-visualtracking-marcos_pieras-2017.pdf)
  * David Pascual 
* Read one paper:
  * [Efficient Deep Learning for Stereo Matching](https://www.cs.toronto.edu/~urtasun/publications/luo_etal_cvpr16.pdf)

##### Efficient Deep Learning for Stereo Matching
They propose a new approach that speeds up the time of a Neural Network to process distances from a minute to less than a second (GPU time). They use a siamese architecture as is standard for this challenges and treat the problema as a multiclass classification. The classes are all the posible disparities.

The problem of distance detection has always been high due its enormus amount of applications in the industry for automation, being the cameras the cheapest sensor compared to others such as LIDAR. This approaches for stereo camera find an interest patch in the  left image and find the probability of a patch in the right image to be the same one. In this paper they try to do this matching by using CNN (convolutional neural networks).

Other approaches further process with more layers after at the exit of the siamese network but they just compute a simple cost-function to compute the iner product on the representation of both images to know the matching score.

Training: For the left image they take random patches for which the ground-truth is known. They size of those patches is the same as the size of the network receptive field. For the right size however they take a bigger patch. Having a 64-dimensional output for the left size and a |yi|x64 dimensional one for the right one. (if I'm not wrong |yi| is all the possible disparities.

Testing: For testing the network computes the 64 dimensional feature for every pixel in the image (only once to maintain efficiency)

#### Week 3 (23/11/2017 - 29/11/2017)

#### Week 2 (16/11/2017 - 22/11/2017)

#### Week 1 (09/11/2017 - 15/11/2017): Starting research
For this first week I had two task that could be differentiated:
* Test some of the examples the JdeRobot framework.
  * Installation: No problema at all with the installation of the framework, I did it with the .deb packages and as I use Ubuntu 16.04 everything went as planned.
  * Cameraserver: Here I found a major hardware problem, my desktop doesn't have a camera so is kind of difficult to use this examples without it. I'll try to get one for the next week so I can try this.
  * Turtlebot + KobukiViewer: I'm still struggling with this example. Y get the following error <nowiki>/usr/include/IceUtil/Handle.h:46: IceUtil::NullHandleException</nowiki> in the next days I'll try  to solve it.
  * ArDrone + UAVViewer: Works perfectly out-of-the-box, I've been flying the drone over the scenario, it's a bit tricky but everything worked correctly.
* Read the thesis of two former students of the course.
  * [Alberto Martín](https://gsyc.urjc.es/jmplaza/students/tfm-visualslam-alberto_martin-2017.pdf)
  * [Marcos Pieras](https://gsyc.urjc.es/jmplaza/students/tfm-visualtracking-marcos_pieras-2017.pdf)


