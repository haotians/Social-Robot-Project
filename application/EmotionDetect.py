# coding=utf-8
# Author: Haotian Shi, Last Modified Date: 2016-02-17
# Author: Yehang Liu, Last Modified Date: 2016-02-18
import numpy as np
import string
import time
import os
import cv2

import components.Components as Components
from library.vision.HammingMarker.MarkerDetect import detect_markers
from library.vision.HammingMarker.HammingMarker import HammingMarker
from library.vision.CameraSupport.CameraControl import open_camera, release_camera
import library.vision.face_information.face_info_api as face_info_api

SLEEP_TIME = 0.2
speak_interval = 3

class EmotionDetection(Components.Node):
    def __init__(self, master_object, video):
        Components.Node.__init__(self, master_object)
        self.video = video

    def _node_run(self):
        emotion_detector = face_info_api.DeepFaceInfo(False,'emotion',
                                                      'library/vision/face_information/')
        cap = self.video
        k = 0
        speak_valid = True
        speak_marker = 0
        while self.thread_active:

            #1 report
            self.output_status_to_master(False)

            #2 check input
            ret, img = cap.read()

            speak_valid = self.speak_validation(speak_valid, speak_marker)

            if k % 6 == 0 and speak_valid is True:

                k = 0

                #3 process message
                labels, confidences = emotion_detector.face_info_extract(img,None,5,None)

                print labels, confidences

                # protect invalid img
                if labels is None:
                    time.sleep(SLEEP_TIME)
                    continue

                txt_refined, confidence_refined = self.post_porcess(labels[0], confidences[0])

                txt = txt_refined[0]
                confidence = confidence_refined[0]
                #4 output data to the linked topics
                data = None
                if confidence > 0.75:
                    print "confidence and class and time consumption: ", confidence,txt
                    if cmp(txt,'Happy') == 0:
                        data = '你看起来很高兴呀'
                        print "detect Happy emotion"
                    elif cmp(txt, 'unhappy') == 0:
                        data = '我觉得你心情不好,要不要和我说说话'
                    elif cmp(txt, 'Surprise') == 0:
                        data = '发生了什么事情,让你大吃一惊'
                    if data is not None:
                        message = self.message_object.message_warp("voice_data", data)
                        self.output_all_messages([message])
                        speak_valid = False
                        speak_marker = time.time()
            k = k + 1

            time.sleep(0.01)

        release_camera(cap)

    def speak_validation(self, speak_valid_flag, speak_marker):
        if speak_valid_flag is True:
            return True
        else:
            if time.time() - speak_marker > speak_interval:
                return True
            else:
                return False

    def post_porcess(self, labels, confidences):
        out_label = []
        out_confidence = []
        for label in labels:
            if out_label.count(label) == 0:
                confidence = 0
                out_label.append(label)
                all_index = self.find_all_index(labels, label)
                for index in all_index:
                    # print "index and confidences: ",index,confidences
                    confidence = confidence + confidences[index]
                out_confidence.append(confidence)
        return out_label, out_confidence

    def find_all_index(self, array_list, item):
        return [i for i, a in enumerate(array_list) if a == item]

