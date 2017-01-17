# coding=utf-8
# Author: Yehang Liu, Last Modified Date: 2016-02-17
# import threading

import library.vision.Vision.FaceDetect as detect
import components.Components as Components

import time
import os
import numpy as np
import cv2
import library.vision.facedirection.FaceDirectionPrediction as face_pos_detector
import dlib
import math


sleep_time = 1
track_gap = 20


class PersonTrack(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)
        self.detector = None
        self.face_pos_detector = None

    def read_sensor_data(self):
        robot_position = None
        move_stage = None

        # read messages from all topics
        messages = self.get_messages_from_all_topics()

        for one_message in messages:
            # position messages
            if one_message[1] == 71:
                robot_position = one_message[2]
            # movement stage
            elif one_message[1] == 83:
                print "robot move stage received"
                move_stage = one_message[2]
            # other info won't processed
            else:
                continue
        # protection
        if robot_position is None or move_stage is None:
            return None, None
        else:
            return robot_position, move_stage

    def check_move_stage(self, move_stage):

        if move_stage > 0:
            return False
        else:
            return True


    def _node_run(self):
        print 'start to track'
        # init system
        fx , cx = self.init_sys()
        time.sleep(1)

        print "done init"
        faces = None

        # target_position = None

        while self.thread_active:

            # report to master
            self.output_status_to_master(False)

            # read msg from topics, ie data fro this app
            robot_position, move_stage = self.read_sensor_data()

            # # check targte position lock
            # if not self.check_position(robot_position, target_position) and target_position is not None:
            #     # failed check
            #     print "haven't reached target destination, continue working"
            #     time.sleep(sleep_time)
            #     continue

            # check movement stage and robot position info, if failed check, continue the loop
            if not self.check_move_stage(move_stage) or robot_position is None:
                print "failed the check, not converge to target position yet"
                time.sleep(sleep_time)
                continue

            # pass the check
            # face detect from dlib
            try:
                frame, faces = self.face_detect()
            except:
                print "failed to detect face from frame"
                time.sleep(sleep_time)
                continue

            face_number = faces.shape[0]

            # can't find face or too many faces, continue
            if face_number == 0 or face_number > 1:
                print "can't find a face or too many faces in the frame, so i wait one second for a new img"
                time.sleep(sleep_time)
                continue

            # calculate face orientation
            face_angles = self.face_pos_detector.predict(frame, faces, False)
            # wait a littile be for caffe to release memory
            time.sleep(0.1)

            angle_yaw_degree = face_angles[0][1]

            if abs(angle_yaw_degree)< 10:
                angle_yaw_degree = 0

            # only one face founded

            # get value
            angle_yaw = float(angle_yaw_degree*math.pi/180)
            face_position = faces[0]

            # data swap
            temp = face_position[1]
            face_position[1] = face_position[2]
            face_position[2] = temp

            # start counting time
            self.track_flag = time.time()
            face_angle, theta_offset, distance = self.data_process(angle_yaw, face_position, fx, cx)

            # angle offset tolerance
            if abs(theta_offset)< 15*180/math.pi:
                theta_offset = 0

            print "pitch_angle, theta, distance: ", angle_yaw*180/math.pi, theta_offset*180/math.pi, distance
            # calculate target position
            target_position = self.coordinate_conversion(distance, theta_offset, angle_yaw, robot_position)
            print "target position: ", target_position
            print "current position: ", robot_position
            # output position
            message = []
            out_pos = [3] + target_position
            message.append(self.message_object.message_warp('wheel_command', out_pos))
            print "msg to wheel:", message
            self.output_all_messages(message)

            time.sleep(sleep_time)

        print 'finish track'

    def init_sys(self):

        # pcm = PCM.PythonCallMatlab()  # face direction
        # self.fdc = None
        self.detector = detect.FaceDetector()
        # self.detector.select_trained_cascade_model("./library/vision/Vision/cascade_models/haarcascade_profileface.xml")
        path = os.getcwd()

        # todo: cpu memory costs too much, leave it here
        deploy_file = path + '/library/vision/facedirection/model/deploy.prototxt'
        model_file = path + '/library/vision/facedirection/model/68point_dlib_with_pose.caffemodel'
        mean_file= path +'/library/vision/facedirection/model/VGG_mean.binaryproto'
        self.face_pos_detector = face_pos_detector.FacePosDetector(deploy_file,model_file,mean_file)

        fx, cx = self.read_calibration()
        return fx,cx

    def face_detect(self):
        path = os.getcwd()
        frame = cv2.imread(path + '/library/vision/facedirection/saved.jpg')

        # cv2.imshow('input',frame)
        # cv2.waitKey(0)

        detector = dlib.get_frontal_face_detector()
        dets = detector(frame)
        bboxs = np.zeros((len(dets),4))
        for i, d in enumerate(dets):
            bboxs[i,0] = d.left()
            bboxs[i,1] = d.right()
            bboxs[i,2] = d.top()
            bboxs[i,3] = d.bottom()
        return frame, bboxs

    def sideview_detect(self):

        path = os.getcwd()

        frame = cv2.imread(path + '/library/vision/facedirection/saved.jpg')

        # frame = cv2.imread('./library/vision/facedirection/save.jpg')

        cv2.imshow('input', frame)
        cv2.waitKey(0)

        frame_reverse = cv2.flip(frame, 1)
        faces, gray = self.detector.face_cascade_detect(frame)
        faces_reverse, gray = self.detector.face_cascade_detect(frame_reverse)

        print len(faces),len(faces_reverse)

        if len(faces) is 1 and len(faces_reverse) is 0:
            return frame, faces
        elif len(faces) is 0 and len(faces_reverse) is 1:
            return frame, faces_reverse
        else:
            print "can't find a face!"
            return frame, None

    def client_receive_message(self):
        flag = self.sideview_detect()
        if flag is False:
            pass
        elif flag is True:
            self.sock.send("1")
            return self.sock.recv(23)
        else:
            self.sock.send("2")
            self.sock.close()

    def convert_data(self, mat_return):
        position = [0, 0, 0, 0]
        index = -1
        if len(mat_return) != 23 or len(mat_return[0:3]) != 3 or len(mat_return[5:8]) != 3 or len(mat_return[10:13]) !=\
                3 or len(mat_return[15:18]) != 3 or len(mat_return[20:23]) != 3:
            ori_x0 = 0
            ori_x1 = 0
            ori_y0 = 0
            ori_y1 = 0
        else:
            index = int(100 * round(float(mat_return[0])) + 10 * round(float(mat_return[1])) +
                        round(float(mat_return[2]))) - 112
            ori_x0 = int(100 * round(float(mat_return[5])) + 10 * round(float(mat_return[6])) +
                         round(float(mat_return[7]))) - 112
            ori_y0 = int(100 * round(float(mat_return[10])) + 10 * round(float(mat_return[11])) +
                         round(float(mat_return[12]))) - 112
            ori_x1 = int(100 * round(float(mat_return[15])) + 10 * round(float(mat_return[16])) +
                         round(float(mat_return[17]))) - 112
            ori_y1 = int(100 * round(float(mat_return[20])) + 10 * round(float(mat_return[21])) +
                         round(float(mat_return[22]))) - 112
        mat_angle = index
        if mat_angle == 0:
            mat_angle = 90
        elif mat_angle == 3:
            mat_angle = 45
        elif mat_angle == 9:
            mat_angle = -45
        elif mat_angle == 12:
            mat_angle = -90
        else:
            mat_angle = -1
        position[0] = int(4.8 * ori_x0)
        position[1] = int(4.8 * ori_y0)
        position[2] = int(4.8 * ori_x1)
        position[3] = int(4.8 * ori_y1)
        return mat_angle, position

    def data_process(self, face_angle, position, fx, cx):

        distance, face_dis_str = self.detector.face_distance_mat(position)
        face_center = (position[0] + position[2]) / 2
        theta_offset = np.arctan((face_center - cx) / fx)
        return face_angle, theta_offset, distance

    def read_calibration(self):

        path = os.getcwd()
        path = path + '/library/vision/CameraSupport/calibration_matrix.txt'

        file = open(path, 'r')
        text = ['']
        text[0] = file.readline()
        file.close()
        temp = text[0].split()
        fx = float(temp[0])
        cx = float(temp[2])
        return fx, cx

    def coordinate_conversion(self, dis, theta_picture, theta_face_direction, origin):
        # origin [0,1,2] x y theta

        # calculate the transformation matrix, from robot to origin world coordinate
        matrix_transformation = np.array([[np.cos(origin[2]), -np.sin(origin[2]), origin[0]],
                           [np.sin(origin[2]), np.cos(origin[2]), origin[1]],
                           [0, 0, 1]])

        theta_a = theta_picture + math.pi - theta_face_direction

        # transformation matrix from person to robot
        matrix_mid = np.array([[np.cos(theta_a), -np.sin(theta_a), dis * np.cos(theta_picture)],
                           [np.sin(theta_a), np.cos(theta_a), dis * np.sin(theta_picture)],
                           [0, 0, 1]])

        matrix_t = np.array([[dis, 0, 1]])
        t_matrix_t = matrix_t.T
        temp = np.dot(matrix_transformation, matrix_mid)
        matrix_goal = np.dot(temp, t_matrix_t)
        t_matrix_goal = matrix_goal.T

        x_goal = t_matrix_goal[0][0]
        y_goal = t_matrix_goal[0][1]

        theta_b = origin[2] + theta_picture - theta_face_direction
        target_coordinate = [x_goal, y_goal, theta_b]
        return target_coordinate

    def check_position(self, current_pos, target_pos):
        XY_couple_tolerance = 0.2
        theta_tolerance = 0.03

        error = None
        if target_pos is not None:
            error = [target_pos[0]-current_pos[0],
                     target_pos[1]-current_pos[1],
                     target_pos[2]-current_pos[2]]
        else:
            return False
        # check error, return true if tolerance is reached
        print "error x: ", error[0]
        print "error y: ", error[1]
        print "error z: ", error[2]

        if (abs(error[0]) + abs(error[1]) ) < XY_couple_tolerance and abs(error[2]) < theta_tolerance:
            time.sleep(0.5)
            return True
        else:
            return False

if __name__ == '__main__':

    a = [1,2,3]
    b=[1,1,1]
    print a + b

    deploy_file =  '../library/vision/facedirection/model/deploy.prototxt'
    model_file = '../library/vision/facedirection/model/68point_dlib_with_pose.caffemodel'
    mean_file= '../library/vision/facedirection/model/VGG_mean.binaryproto'
    face_pos_detector = face_pos_detector.FacePosDetector(deploy_file,model_file,mean_file)

    # import subprocess as sp
    #
    # cur_path = os.path.dirname(os.path.realpath(__file__))
    #
    # command = "python ../library/vision/facedirection/FaceDirectionPrediction.py"
    # print command
    # sub_process = sp.Popen(command,
    #                        shell=True,
    #                        stdout=sp.PIPE,
    #                        stderr=sp.STDOUT)



    # master = Components.Master()
    # pt = PersonTrack(master)
    # # pt._node_run()
    # pt.init_sys()
    # print pt.sideview_detect()
    # pt._node_run()

