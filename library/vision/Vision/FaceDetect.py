# coding=utf-8
# Author: Yehang Liu, Last Modified Date: 2016-02-17
import cv2
import numpy as np
import math

class FaceDetector(object):
    def __init__(self):
        self.cascade_model = None
        self.select_trained_cascade_model(None)

    def select_trained_cascade_model(self,path=None):
        if path is None:
            path = "library/vision/Vision/cascade_models/haarcascade_frontalface_alt2.xml"
            # path = "cascade_models/haarcascade_frontalface_alt2.xml" # local use
            # path = "/usr/local/share/OpenCV/cascade_models/haarcascade_frontalface_alt2.xml"
        self.cascade_model = cv2.CascadeClassifier(path)
        # return cascade_model

    def face_cascade_detect(self, img):
        # opencv based viola jones face detector
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
        faces = self.cascade_model.detectMultiScale(gray_normal, scaleFactor=1.3,
                                               minNeighbors=4, minSize=(30, 30),
                                               flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
                                               # flags=cv2.cv.CV_HAAR_FEATURE_MAX)
        # avoid null pointer
        if len(faces) > 0:
            # reshape the data from [x0 y0 w h] to [x0 y0 x1 y1]
            faces[:, 2:4] += faces[:, 0:2]
        return faces, gray

    def face_joint_cascade(self, img):
        pass

    def face_pos_estimate(self, face_position):
        relative_distance = []
        distance_return = []
        relative_angle = []
        face_length = len(face_position)
        # print "data, ", face_position[0][0]
        for i in range(face_length):
            width = float(face_position[i][2] - face_position[i][0])
            # distance hacked!!!!
            distance = 100 / width + 0.2
            dis = float('%0.2f' % distance)
            # print distance
            angle = self.face_angle_estimate(face_position[i])
            # print angle
            distance_return.append(dis)
            relative_distance.append(str(dis)+"m")
            relative_angle.append(str(angle))
        return distance_return, relative_distance, relative_angle

    def face_angle_estimate(self,face):
        x = float(face[0])
        w = float(face[2]-face[0])
        deviation = (x + w / 2)-320
        # print "deviation is :" , deviation
        angle = int((math.atan(((x + w / 2) - 320) / 1024) * 180 / math.pi))   # -left + right
        return angle

    def face_distance_mat(self, position):
        width = float(position[2] - position[0])
        distance = 100 / width + 0.2
        dis = float('%0.2f' % distance)
        dis_meter = str(dis)+"m"
        return dis, dis_meter