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
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)
        self.name = 'marker'

    def _node_run(self):
        print('marker detection start')

        camera_num = 1
        cap = None
        cap = open_camera(cap, None, camera_num)

        intrinsic_parameter = np.zeros((3, 3), np.float32)
        a = [0, 1, 2]
        homedir = os.getcwd()
        print homedir
        with open(homedir + '/library/vision/CameraSupport/calibration_matrix_c310_2_1280x720.txt') as fd:
            for n, line in enumerate(fd):
                if n in a:
                    intrinsic_parameter[n] = [string.atof(line.split()[0]), string.atof(line.split()[1]),
                                              string.atof(line.split()[2])]

        cam_matrix = intrinsic_parameter
        # skip the first 3 rows to get dist information
        dist = np.loadtxt(homedir + '/library/vision/CameraSupport/calibration_matrix_c310_2_1280x720.txt', dtype=None, skiprows=3)

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
                    # print data, "marker"
                    if msg_type == 93:
                        arm_move = data[0]

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
                id_4_voice = marker.highlite_marker(img, potential_flag=0)

            for potential_marker in potential_markers:
                potential_marker.highlite_marker(img, potential_flag=1)

            cv2.imshow('Test Frame', img)
            cv2.waitKey(10)
            # press q the loop will stop
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
            # release_camera(cap)

            ######
            print "id_4_voice :", id_4_voice
            # print "distance:", distance

            # 3 output data if necessary
            if arm_move == 1 and distance != [0, 0, 0]:
                arm_move = 0

                arm_command = [16] + distance + [0] * 9
                message_out = [self.message_object.message_warp('arm_command', arm_command)]
                print message_out

                self.output_all_messages(message_out)
            # 4 report to master
            self.output_status_to_master(False)

            time.sleep(0.2)


    def marker_detect(self, cam_matrix = None):
        """
        once started, press q the loop will stop
        :param cam_matrix: camera calibration matrix 3-by-3
        :return: None
        """
        # Create video capture object
        camera_num = 0
        cap = None
        cap = open_camera(cap, None, camera_num)

        intrinsic_parameter = np.zeros((3, 3), np.float32)
        a = [0, 1, 2]

        with open('./CameraSupport/calibration_matrix.txt') as fd:
            for n, line in enumerate(fd):
                if n in a:
                    intrinsic_parameter[n] = [string.atof(line.split()[0]), string.atof(line.split()[1]),
                                              string.atof(line.split()[2])]

        cam_matrix = intrinsic_parameter
        # skip the first 3 rows to get dist information
        dist = np.loadtxt('./CameraSupport/calibration_matrix.txt', dtype=None, skiprows=3)
        # print "cam_matrix:\n", cam_matrix
        # print "dist:\n", dist
        while cap.isOpened():
            # Read image and convert to grayscale for processing
            ret, img = cap.read()
            markers, potential_markers, distance = detect_markers(img, cam_matrix, dist)

            for marker in markers:
                marker.highlite_marker(img, potential_flag=0)

            for potential_marker in potential_markers:
                potential_marker.highlite_marker(img, potential_flag=1)

            cv2.imshow('Test Frame', img)
            # press q the loop will stop
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break
        return distance
        release_camera(cap)

    def marker_generate(self, marker_id = None):
        """
        :param marker_id: valid number is 1:4096
        :return: None
        """
        if marker_id is None:
            marker_id = 1
        marker = HammingMarker(marker_id)
        target =  marker.generate_image()
        cv2.imshow('marker', target)
        cv2.waitKey(1000)
        cv2.imwrite('marker_{}.png'.format(marker.id), target)
        cv2.waitKey(10)
        print("Generated Marker with ID {}".format(marker.id))

# if __name__ == '__main__':
#     master = Components.Master
#     marker = Marker(master)
#     marker.marker_generate(3)
