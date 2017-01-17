# How to use ROS and ROSwebtools to stream video via websocket

## Requirement

1. Ubuntu 14.04.4
2. ROS indigo
3. roswebtools (rosbridge_suite and web_video_server)
4. opencv

## Install required packages

### Install ROS

[Indigo installation](http://wiki.ros.org/indigo/Installation/Ubuntu), please install the full package

    sudo apt-get install ros-indigo-desktop-full

make sure you follow the instruction closely and setup the ros path properly

### Install rosbridge_suite and web_video_server

[refer to this page](https://github.com/robotwebtools)

    sudo apt-get install ros-indigo-web-video-server 
    sudo apt-get install ros-indigo-rosbridge-suite 

### Install other dependencies

Other dependencies are most likely included in ROS installation, if not, try to install the following packages 

    sudo apt-get install ros-indigo-catkin
    sudo apt-get install ros-indigo-cv-bridge

## Setup the environment

### Use catkin to create the workspace

[refer to this page](http://wiki.ros.org/catkin/Tutorials/create_a_workspace)


### Use catkin to create the ros package

navigate to the `\src` folder in your catkin workspace, then

    catkin_create_pkg cv_ros rospy std_msgs sensor_msgs cv_bridge

### Copy the source and launch file to proper place

copy `test.launch` to the root of catkin workspace

copy `cv_ros.py` to `src\cv_ros\src` folder


## Build and Run

run `catkin_make` in the root of catkin workspace

source the `setup.sh` in the `devel` folder

run the launch file

    roslaunch test.launch


## Check the video

`http://localhost:8080/stream_viewer?topic=image_topic_2` or
 `<your ip>:8080/stream_viewer?topic=image_topic_2`


## Additional reference

see the zip file, which is an example of catkin workspace, but you cannot directly use it 