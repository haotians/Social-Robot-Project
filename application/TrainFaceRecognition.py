# coding=utf-8
# Author: Yehang Liu, Last Modified Date: 2016-02-18

import os
import time
import locale
import numpy as np

import cv2

from library.vision.Vision import FaceRecognizer
from library.vision.Vision import FaceDetect
import components.Components as Components
import library.vision.face_information.face_info_api as face_info

waiting_time_ddl = 20
waiting_motion_ddl = 32

class TrainFaceRecognition(Components.Node):

    def __init__(self, master_object, cap):
        Components.Node.__init__(self, master_object)
        self.images = []
        self.cap = cap
        self.user_name = None
        self.process_flag = False
        self.waiting_marker = time.time()
        self.motion_marker = None

    def _node_run(self):
        print "start to train the face model"
        stage = 0
        path = 'library/vision/face_recognition/'
        voice_guide = self.read_text(path)
        gender_recognizer, face_detector, face_recognizer = self.init_detectors(path)

        while self.thread_active:

            # report to master
            self.output_status_to_master(False)

            # process messages
            stage, messages = self.process_messages(stage, voice_guide,
                                             gender_recognizer, face_detector, face_recognizer, path)

            # send messages to voice
            self.output_all_messages(messages)

            time.sleep(0.01)

        print 'train new person thread has been stopped'

    def read_text(self, path):
        filename = 'AddNewPerson.txt'

        path_new = path + filename
        length = self.text_length(path_new)
        temp = [''] * length
        file = open(path_new)

        for i in range(0, length):
            temp[i] = file.readline()

        file.close()

        return temp

    def text_length(self, path):
        counter = 0
        file = open(path, 'r')
        while True:
            if file.readline():
                counter += 1
            else:
                file.close()
                break
        return counter

    def init_detectors(self, path):
        gender_recognizer = face_info.DeepFaceInfo(False, 'gender',
                                                   'library/vision/face_information/')
        face_detector = FaceDetect.FaceDetector()
        face_detector.select_trained_cascade_model("library/vision/Vision/cascade_models/"
                                                   "haarcascade_frontalface_alt2.xml")
        face_recognizer = FaceRecognizer.FaceRecognizer(path)

        return gender_recognizer, face_detector, face_recognizer

    def process_messages(self, stage, voice_guide,
                         gender_recognizer, face_detector, face_recognizer, path):

        messages = self.get_messages_from_all_topics()
        msg_out = [self.message_object.message_warp('no_command', 0)]
        data = 0
        for i in range(len(messages)):
            if messages[i] is not None:
                time_marker, msg_type, data, source = self.message_object.message_dewarp(messages[i])
                if msg_type is 61:
                    if data[0] is 2:
                        self.process_flag = True
        if (time.time() - self.waiting_marker) > waiting_time_ddl:
            self.process_flag = True
        if self.process_flag is True:
            stage, msg_out = self.stage_process(data, stage, voice_guide,
                               gender_recognizer, face_detector, face_recognizer, path)
            self.process_flag = False
            self.waiting_marker = time.time()

        return stage, msg_out

    def stage_process(self, data, stage, voice_guide,
                                                                                   gender_recognizer, face_detector, face_recognizer, path):
        msg_out = []

        if stage is 0:
            self.user_name = data[1]
            msg_out.append(self.message_object.message_warp('voice_data', voice_guide[0], 'train_face'))
            msg_out.append(self.arm_actions(stage))
            stage += 1
            self.motion_marker = time.time()
        elif stage < 4:
            self.capture_photos(stage, face_detector, path, voice_guide)
            while time.time() - self.motion_marker < waiting_motion_ddl:
                time.sleep(1)
                continue
            self.motion_marker = time.time()
            stage += 1
            if stage is 4:
                label = self.gender_identification(gender_recognizer)
                if cmp(label, 'Male') == 0:
                    sentence = voice_guide[stage - 1]
                else:
                    sentence = voice_guide[stage]
                msg_out.append(self.message_object.message_warp('voice_data', sentence, 'train_face'))
            else:
                msg_out.append(self.message_object.message_warp('voice_data', voice_guide[stage-1], 'train_face'))
                msg_out.append(self.arm_actions(stage))
        elif stage is 4:
            face_recognizer.train_face_model(path, None)
            msg_out.append(self.message_object.message_warp('voice_data', voice_guide[5], 'train_face'))
            msg_out.append(self.arm_actions(stage))
            stage += 1
        elif stage is 5:
            msg_out.append(self.message_object.message_warp('control_data', 1))

        return stage, msg_out

    def capture_photos(self, stage, face_detector, path, voice_guide):
        capture_num = 5
        stage -= 1
        frame_skip = 4
        counter_frame = 0
        path = path + self.user_name
        flag_save = False
        if not os.path.exists(path):
            os.mkdir(path)
        for i in range(capture_num):
            while self.cap.isOpened():
                ret, img = self.cap.read()
                if not ret:
                    continue
                faces, gray = face_detector.face_cascade_detect(img)
                faces_length = len(faces)
                if faces_length < 1 or faces_length > 1:
                    continue
                if counter_frame == frame_skip:
                    counter_frame = 0
                    x0, y0, x1, y1 = faces[0]
                    # get the face img
                    face = gray[y0:y1, x0:x1]
                    face_reshape = cv2.resize(face, (92, 112), interpolation=cv2.INTER_CUBIC)
                    if stage is 0 and i is 0:
                        self.images.append(face_reshape)
                        flag_save = True
                    else:
                        flag_save = self.image_validation(self.images, face_reshape)
                    if flag_save is True:
                        print (i + stage * capture_num)
                        if (i + stage * capture_num) is 12:
                            rand_speak = np.random.random()
                            if rand_speak > 0.5:
                                sentence = voice_guide[6]
                            else:
                                sentence = voice_guide[7]
                            message = [self.message_object.message_warp('voice_data', sentence)]
                            self.output_all_messages(message)
                        self.images.append(face_reshape)
                        cv2.imwrite(path + "/" + str(i + stage * capture_num)+".png", face_reshape)
                        print stage * capture_num + i, ' is done'
                        break
                    cv2.waitKey(10)
                    flag_save = False

                counter_frame += 1
                cv2.waitKey(30)

    def corr2(self, im1, im2):
        row, col = np.shape(im1)

        part_upper = 0
        part_lower_im1 = 0
        part_lower_im2 = 0
        mean_im1 = np.mean(im1)
        mean_im2 = np.mean(im2)

        for i in range(row):
            for j in range(col):
                part_upper += (im1[i][j] - mean_im1) * (im2[i][j] - mean_im2)
                part_lower_im1 += (im1[i][j] - mean_im1) ** 2
                part_lower_im2 += (im2[i][j] - mean_im2) ** 2
        try:
            corr = part_upper / np.sqrt(part_lower_im1 * part_lower_im2)
        except:
            corr = 0
        corr = float('%0.3f' %corr)
        return corr

    def image_validation(self, faces, face_current):
        temp = []
        for i in range(len(faces)):
            temp = faces[i]
            corr_efi = self.corr2(temp, face_current)
            if corr_efi < 0.75:
                return True
        return False

    def gender_identification(self, gender_recognizer):
        loop_time = 5
        labels = [''] * loop_time

        for i in range(loop_time):
            success, image = self.cap.read()
            labels_temp, confidence = gender_recognizer.face_info_extract(image, None, 2, None)

            if labels_temp is None:
                if i is loop_time - 1:
                    label = 'Female'
                    break
                continue

            labels[i] = labels_temp[0][0]

            if confidence > 0.9:
                label = labels[i]
                break

            if i is (loop_time - 1):
                if labels.count(labels[0]) > loop_time / 2:
                    label = labels[1]
                else:
                    if cmp(labels[0], 'Female') == 0:
                        label = 'Male'
                    else:
                        label = 'Female'
        return label

    def arm_actions(self, stage):
        arm_trajectory = {
            0: [2, './data/arm_trajectory/game_1', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            2: [2, './data/arm_trajectory/game_2', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            3: [2, './data/arm_trajectory/game_3', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            4: [11, 0, 0, 0, 0, 0, 0, 0, 0, 0,  0, 0, 0]
        }.get(stage)
        print 'motion stage: ', stage
        return self.message_object.message_warp('arm_command', arm_trajectory)

