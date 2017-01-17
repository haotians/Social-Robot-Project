# coding=utf-8
# Author: Yehang Liu, Last Modified Date: 2016-02-18


import sys

import cv

from MarkerAPI import *
from library.vision.Vision.FaceRecognitionAPI import draw_face
import FaceDetect
import FaceRecognizer
import components.Components as Components
import os
import numpy as np


class Vision(Components.Node):
    def __init__(self, master_object, video):
        Components.Node.__init__(self, master_object)
        self.video = video
        self.use_pipe = False
        self.time_marker_list = []
        self.name_list = []
        self.face_detector = None
        self.face_recognizer = None
        self.static_list = []
        self.frame_counter = 0
        self.valid_speak_frame = 7
        self.init_flag = True
        self.save_marker = time.time()

    def source_camera(self):
        self.use_pipe = False

    def source_pipe(self):
        self.use_pipe = True

    def _node_run(self):
        print 'start vision sys'
        vision_flag = True
        speak_validation_flag = False
        self.init_vision()
        while self.thread_active:

            # main process

            message_out = []

            self.process_images(vision_flag, message_out)
            self.frame_counter += 1

            # send messages

            if len(message_out) > 0:
                self.output_all_messages(message_out)

            # report to master

            self.output_status_to_master(False)

        print 'vision thread has been stopped'

    def ar_video_for_ui(self):
        cap = cv.CaptureFromCAM(0)
        if not cap:
            sys.stdout.write("failed CaptureFromCAM")
        while True:
            if not cv.GrabFrame(cap):
                break
            frame = cv.RetrieveFrame(cap)
            sys.stdout.write(frame.tostring())

    def say_hello(self,face_name):

        speak_validation_flag = self.speak_validation(face_name)
        message = self.message_object.message_warp('no_command', 0)

        if cmp(face_name, ['Not in the data base']) is not 0:
            if face_name not in self.name_list and speak_validation_flag is True:
                time_marker_temp = time.time()
                self.time_marker_list.append(time_marker_temp)
                self.name_list.append(face_name)
                sentence = self.greeting_sentence(face_name[0])
                message = self.message_object.message_warp('voice_data',sentence)


            time_marker_temp = time.time()
            for i in range(len(self.name_list)):
                if time_marker_temp - self.time_marker_list[i] > 5:
                    self.time_marker_list[i] = []
                    self.name_list[i] = []

            counter = self.time_marker_list.count([])

            for i in range(counter):
                self.time_marker_list.remove([])
                self.name_list.remove([])
        return message

    def speak_validation(self, name):

        speak_valid_flag = False

        if cmp(name, ['Not in the data base']) is not 0:
            if len(self.static_list) > 0:
                for i in range(len(self.static_list)):
                    if cmp(name, self.static_list[i][0]) is 0:
                        self.static_list[i][1] += 1
                        break
            else:
                self.static_list.append([name, 1, self.frame_counter])

        if len(self.static_list) > 0:
            for i in range(len(self.static_list)):
                temp = self.static_list[i][2]
                if self.static_list[i][1] > self.valid_speak_frame and self.frame_counter - self.static_list[i][2] < 10:
                    speak_valid_flag = True
                    self.static_list[i] = []
                elif self.frame_counter - temp > 10:
                    self.static_list[i] = []

        counter = self.static_list.count([])

        for i in range(counter):
            self.static_list.remove([])

        if self.frame_counter > 511:
            self.frame_counter = 0
            self.static_list = []
            speak_valid_flag = False

        return speak_valid_flag

    def process_images(self, vision_flag, message_out):
        if vision_flag is True:
            face_name = []
            face_dis = []
            # read frame
            success, frame = self.video.read()
            # protect invalid reading
            if not success:
                return

            if time.time() - self.save_marker > 1:
                self.save_marker = time.time()
                path = os.getcwd()
                cv2.imwrite(path + '/library/vision/facedirection/saved.jpg', frame)
                time.sleep(0.1)

            # detect faces
            faces, gray = self.face_detector.face_cascade_detect(frame)
            faces_length = len(faces)
            if faces_length is 1:

                face_name = self.face_recognizer.face_recognition(gray, faces)
                message_out.append(self.say_hello(face_name))

            elif faces_length > 1:
                face_name = self.face_recognizer.face_recognition(gray, faces)
                distance_return, face_dis, face_angle = self.face_detector.face_pos_estimate(faces)
                for i in range(len(face_name)):
                    message_out.append(self.say_hello([face_name[i]]))

            if faces_length > 0:
                for i in range(faces_length):
                    draw_face(frame, faces[i],None,None)

            # cv2.imshow('video', frame)

            cv2.waitKey(20)

            return message_out

    def init_vision(self):
        # if self.video is None or not self.video.isOpened():
        #     if self.use_pipe:
        #         self.video = open_camera(self.video, None, "outpipe")
        #     else:
        #         self.video = open_camera(self.video)
        self.face_detector = FaceDetect.FaceDetector()
        self.face_detector.select_trained_cascade_model("library/vision/Vision/cascade_models/"
                                                   "haarcascade_frontalface_alt2.xml")
        self.face_recognizer = FaceRecognizer.FaceRecognizer('library/vision/face_recognition/trained_face_model.pkl')

    def greeting_sentence(self, name):
        rand_num = np.random.random()
        if rand_num <= 1.0/3:
            select = 1
        elif rand_num > 1.0/3 and rand_num <= 2.0/3:
            select = 2
        else:
            select = 3

        greetings = {
            1: '你好啊,' + str(name),
            2: str(name) + ',你今天看起来不错',
            3: str(name) + ',又见到你了'
        }.get(select)

        return greetings