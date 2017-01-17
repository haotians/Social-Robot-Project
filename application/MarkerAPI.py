# coding=utf-8
# Author: Shenchuan Liu, Last Modified Date: 2016-02-17
# Author: Yehang Liu, Last Modified Date: 2016-02-17
import numpy as np
import string
import time
import os
import cv2

import components.Components as Components
from library.vision.HammingMarker.MarkerDetect import detect_markers
from library.vision.HammingMarker.HammingMarker import HammingMarker
from library.vision.CameraSupport.CameraControl import open_camera, release_camera


class Marker(Components.Node):
    def __init__(self, master_object, cap):
        Components.Node.__init__(self, master_object)
        self.name = 'marker'
        self.cap = cap

    def _node_run(self):
        print('marker detection start')

        camera_num = 0
        # cap = None
        # cap = open_camera(cap, [1280, 720], camera_num)

        cap = self.cap

        intrinsic_parameter = np.zeros((3, 3), np.float32)
        a = [0, 1, 2]
        homedir = os.getcwd()
        print homedir
        with open(homedir + '/library/vision/CameraSupport/calibration_matrix_c310_1280x720.txt') as fd:
            for n, line in enumerate(fd):
                if n in a:
                    intrinsic_parameter[n] = [string.atof(line.split()[0]), string.atof(line.split()[1]),
                                              string.atof(line.split()[2])]

        cam_matrix = intrinsic_parameter
        # skip the first 3 rows to get dist information
        dist = np.loadtxt(homedir + '/library/vision/CameraSupport/calibration_matrix_c310_1280x720.txt', dtype=None, skiprows=3)

        arm_move = 0

        while self.thread_active:

            # Part 1: read all message:
            messages = self.get_messages_from_all_topics()

            # Part 2: use these messages to generate commands for each topic

            # Part 2.1: preprocess data, get command for wheel
            current_time = time.time()
            for i in range(len(messages)):
                if messages[i] is not None:
                    msg_time, msg_type, data, source = self.message_object.message_dewarp(messages[i])
                    print data, "marker"
                    if msg_type == 93:
                        arm_move = data

            # 2 process data

            # distance = self.marker_detect()
            ######
            # print "cam_matrix:\n", cam_matrix
            # print "dist:\n", dist
            # while cap.isOpened():

            # Read image and convert to grayscale for processing
            ret, img = cap.read()

            markers, potential_markers, distance = detect_markers(img, cam_matrix, dist)

            id_4_voice = 0
            for marker in markers:
                id_4_voice = marker.id
                marker.highlite_marker(img, potential_flag=0)

            # for potential_marker in potential_markers:
            #     potential_marker.highlite_marker(img, potential_flag=1)
            #

            # cv2.imshow('Test Frame', img)
            # cv2.waitKey(10)
            # press q the loop will stop
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            # release_camera(cap)

            ######
            # print "id_4_voice :", id_4_voice
            # print "distance:", distance

            # 3 output data if necessary
            # distance = [1, 1, 1]

            if arm_move == 1 and distance != [0, 0, 0]:
                arm_move = 0
                arm_command = [17] + distance + [0] * 9
                print arm_command
                message_out = [self.message_object.message_warp('arm_command', arm_command)]
                if id_4_voice == 1625:
                    txt = '我来抱那只小恐龙给你玩吧'
                elif id_4_voice == 2145:
                    txt = '那里有台电子琴，我接着弹琴给你吧'
                elif id_4_voice == 2645:
                    txt = '那我们去沙发那里休息吧'
                else:
                    txt = '...'
                # print "hahaha"
                message_for_voice = self.message_object.message_warp('voice_data', txt)
                message_out.append(message_for_voice)
                self.output_all_messages(message_out)

            # 4 report to master
            self.output_status_to_master(False)

            time.sleep(0.2)
        cap.release()
