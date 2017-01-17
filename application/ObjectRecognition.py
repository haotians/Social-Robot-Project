# coding=utf-8
# Author: Haotian Shi, Last Modified Date: 2016-02-17
# Author: Yehang Liu, Last Modified Date: 2016-02-18
import time
import cv2

import components.Components as Components
import library.vision.object_detect.cnn_object_detection as detector
from library.vision.CameraSupport.CameraControl import open_camera
from library.vision.AI_models.obj_detect_ai import response_api

speak_interval = 5

class ObjectRecognition(Components.Node):
    def __init__(self, master, video):
        Components.Node.__init__(self, master)
        self.video = video
        self.use_pipe = False
        # 200ms per frame, error rate 20%
        # self.detector = detector.CNNDetection(False, 'library/vision/object_detect/models_cnn/NIN/')
        # 500ms per frame, error rate 13%
        self.detector = detector.CNNDetection(False, 'library/vision/object_detect/models_cnn/VGG_S/')

        # 2500ms per frame, error rate 7%
        # self.detector = detector.CNNDetection(False,'object_detect/models_cnn/VGG16/')
        self.valid_class_names = 1

    def post_porcess(self, labels, confidences):
        out_label = []
        out_confidence = []
        for label in labels:
            if out_label.count(label) == 0:
                confidence = 0
                out_label.append(label)
                all_index = self.find_all_index(labels, label)
                for index in all_index:
                    confidence = confidence + confidences[index]
                out_confidence.append(confidence)
        return out_label, out_confidence

    def find_all_index(self, array_list, item):
        return [i for i, a in enumerate(array_list) if a == item]

    def _node_run(self):

        if self.video is None or not self.video.isOpened():
            if self.use_pipe:
                self.video = open_camera(self.video, None, "outpipe")
            else:
                self.video = open_camera(self.video,  [640, 480])

        candidates_list = []
        candidates_list_size = 3
        tolerance = 2

        allowed_class = ['杯子','花盆','汉堡','键盘',
                         '枕头','大象','玩偶','鱼',
                         '文字','手机','狗','猫',
                         '笔', '花瓶','手表','裤子']

        k = 0
        skip_frame = 10
        speak_valid = True
        speak_marker = 0

        while self.thread_active:

            # report to master
            self.output_status_to_master(False)

            speak_valid = self.speak_validation(speak_valid, speak_marker)

            # read frame
            success, frame = self.video.read()

            k = k+1

            if k % skip_frame == 0:

                if not speak_valid:
                    time.sleep(0.05)
                    continue

                labels, confidence = self.detector.classification(frame)

                labels_final, confidences_final = self.post_porcess(labels, confidence)

                out_label = labels_final[0]

                out_confidence = confidences_final[0]

                # if out_confidence > 0.32:
                #     print "results and confidence: ", out_label, out_confidence

                try:
                    index = allowed_class.index(out_label)
                except:
                    index = None

                if out_confidence > 0.32 and index is not None:
                    print "results and confidence: ", out_label, out_confidence
                    candidates_list.append(out_label)

                if len(candidates_list) >= candidates_list_size:
                    dic = {}
                    # make dic
                    for item in candidates_list:
                        if item in dic.keys():
                            dic[item] += 1
                        else:
                            dic[item] = 1

                    del candidates_list[0]

                    # loop dic
                    for key in dic:
                        if dic[key] > tolerance:
                            out_label = response_api(key)
                            message = self.message_object.message_warp("voice_data", out_label)
                            self.output_all_messages([message])
                            speak_valid = False
                            speak_marker = time.time()
                            candidates_list = []
                            break

                k = 0

            # cv2.imshow('result',frame)
            cv2.waitKey(10)

            time.sleep(0.05)

    def speak_validation(self, speak_valid_flag, speak_marker):
        if speak_valid_flag is True:
            return True
        else:
            if time.time() - speak_marker > speak_interval:
                return True
            else:
                return False
