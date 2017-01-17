# Author: Yehang Liu, Last Modified Date: 2016-02-17
#!/usr/bin/python
# The contents of this file are in the public domain. See LICENSE_FOR_EXAMPLE_PROGRAMS.txt
#
#   This example program shows how to find frontal human faces in an image.  In
#   particular, it shows how you can take a list of images from the command
#   line and display each on the screen with red boxes overlaid on each human
#   face.
#
#   The examples/faces folder contains some jpg images of people.  You can run
#   this program on them and see the detections by executing the
#   following command:
#       ./face_detector.py ../examples/faces/*.jpg
#
#   This face detector is made using the now classic Histogram of Oriented
#   Gradients (HOG) feature combined with a linear classifier, an image
#   pyramid, and sliding window detection scheme.  This type of object detector
#   is fairly general and capable of detecting many types of semi-rigid objects
#   in addition to human faces.  Therefore, if you are interested in making
#   your own object detectors then read the train_object_detector.py example
#   program.
#
#
# COMPILING/INSTALLING THE DLIB PYTHON INTERFACE
#   You can install dlib using the command:
#       pip install dlib
#
#   Alternatively, if you want to compile dlib yourself then go into the dlib
#   root folder and run:
#       python setup.py install
#   or
#       python setup.py install --yes USE_AVX_INSTRUCTIONS
#   if you have a CPU that supports AVX instructions, since this makes some
#   things run faster.
#
#   Compiling dlib should work on any operating system so long as you have
#   CMake and boost-python installed.  On Ubuntu, this can be done easily by
#   running the command:
#       sudo apt-get install libboost-python-dev cmake
#
#   Also note that this example requires scikit-image which can be installed
#   via the command:
#       pip install scikit-image
#   Or downloaded from http://scikit-image.org/download.html.

import sys

import dlib
import cv2
import numpy as np

from FaceRecognitionAPI import draw_face

def face_cascade_detect(img):
    detector = dlib.get_frontal_face_detector()
    # not super good
    gray = None
    # convert to gray scale
    if np.ndim(img) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # as assume single channel data is grayscaled image
    elif np.ndim(img) == 1:
        gray = img
    # normalizes the brightness and increases the contrast of the image
    gray_normal = cv2.equalizeHist(gray)
    # get faces
    faces = []
    pos = detector(gray_normal,1)

    for i, d in enumerate(pos):
        face = [d.left(), d.top(), d.right(), d.bottom()]
        faces.append(face)

    return faces, gray

# main function
def main():
    # Create video capture object
    camera_num = 0
    cap = cv2.VideoCapture(camera_num)
    cap.set(3, 640)
    cap.set(4, 480)

    while cap.isOpened():

        # Read image and convert to grayscale for processing
        ret, img = cap.read()

        faces, gray= face_cascade_detect(img)

        for face in faces:
            draw_face(img, face, None, None)
        # dlib.hit_enter_to_continue()

        cv2.imshow('Test Frame', img)
        cv2.waitKey(10)
        # if cv2.waitKey(1) & 0xFF == ord('q'):
        #     break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    print "start"
    # get_training_data("haotians")
    # train_face_model("/home/haotians/Documents/Github/Vision/ewaybot_vision/face_recognition", face_size)
    main()