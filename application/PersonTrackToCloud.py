# coding=utf-8
import library.vision.Vision.FaceDetect as detect
import components.Components as Components
import time
import os
import numpy as np
import cv2
# import library.vision.facedirection.FaceDirectionPrediction as Face_pos_detector
import dlib
import math
sleep_time = 1


class PersonTrackToCloud(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)
        self.detector = None
        self.face_pos_detector = None

    def _node_run(self):
        print 'start to track'
        # init system
        fx, cx = self.init_sys()
        time.sleep(1)
        print "done init"
        while self.thread_active:
            # report to master
            self.output_status_to_master(False)
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
            # face_angles = self.face_pos_detector.predict(frame, faces, False)
            # wait a littile be for caffe to release memory
            time.sleep(0.1)
            angle_yaw_degree = 1   # just for test
            # angle_yaw_degree = face_angles[0][1]

            if abs(angle_yaw_degree) < 10:
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
            # self.track_flag = time.time()
            face_angle, theta_offset, distance = self.data_process(angle_yaw, face_position, fx, cx)
            angle_theta_offset = theta_offset * 180 / math.pi
            print "angle_theta_offset , distance:", angle_theta_offset, distance
            # angle offset tolerance
            # if abs(theta_offset) < 15*180/math.pi:
            #     theta_offset = 0
            # print "pitch_angle, theta, distance: ", angle_yaw*180/math.pi, theta_offset*180/math.pi, distance
            # # calculate target position
            # target_position = self.coordinate_conversion(distance, theta_offset, angle_yaw, robot_position)
            # print "target position: ", target_position
            # print "current position: ", robot_position
            # # output position
            # message = []
            # out_pos = [3] + target_position
            # message.append(self.message_object.message_warp('wheel_command', out_pos))
            # print "msg to wheel:", message
            # self.output_all_messages(message)
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
        mean_file = path + '/library/vision/facedirection/model/VGG_mean.binaryproto'
        # self.face_pos_detector = Face_pos_detector.FacePosDetector(deploy_file, model_file, mean_file)

        fx, cx = self.read_calibration()
        return fx, cx

    def read_calibration(self):

        path = os.getcwd()
        path += '/library/vision/CameraSupport/calibration_matrix_640.txt'
        files = open(path, 'r')
        text = ['']
        text[0] = files.readline()
        files.close()
        temp = text[0].split()
        fx = float(temp[0])
        cx = float(temp[2])
        return fx, cx

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

    def face_detect(self):
        path = os.getcwd()
        frame = cv2.imread(path + '/library/vision/facedirection/saved.jpg')
        detector = dlib.get_frontal_face_detector()
        dets = detector(frame)
        bboxs = np.zeros((len(dets), 4))
        for i, d in enumerate(dets):
            bboxs[i, 0] = d.left()
            bboxs[i, 1] = d.right()
            bboxs[i, 2] = d.top()
            bboxs[i, 3] = d.bottom()
        return frame, bboxs

    def data_process(self, face_angle, position, fx, cx):

        distance, face_dis_str = self.detector.face_distance_mat(position)
        face_center = (position[0] + position[2]) / 2
        # print "face center and cx: ", face_center, cx
        theta_offset = np.arctan((face_center - cx) / fx)
        return face_angle, theta_offset, distance

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

