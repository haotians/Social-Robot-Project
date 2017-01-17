# coding=utf-8

from __future__ import division
import threading
import math
import os

import cv2
import cv2.cv as cv

from library import gui as fpp
from voice import PyVoice as pv
from legacy import Basic


class FaceDetect(Basic.BasicCommand):

    def __init__(self):
        Basic.BasicCommand.__init__(self)
        self.fpp = fpp.FaceppLib()
        self.count = 0
        self.count_time = 0
        self.frame = None
        self.faces = []
        self.remember_age_gender_result = []
        self.remember_person_name_warn_result = []
        self.face_center_x = []
        self.face_center_y = []
        self.cv_center_x = 0
        self.cv_center_y = 0
        self.res = []
        self.detect = None
        self.file_names = ["temp.jpg", "temp1.jpg", "temp2.jpg", "temp3.jpg", "temp4.jpg"]
        self.distance = 0
        self.distances = {}
        self.font = ()
        self.face_position = []
        self.pv = pv.EWayVoice()
        self.flag_voice_many_people = 0
        self.flag_voice_one_people_l = 0
        self.flag_voice_one_people_y = 0
        self.flag_voice_one_people_unknown = 0
        self.flag_else = True
        self.x = 0
        self.w = 0

        #  edit by lhh, for skip dummy
        self.dummy_center_x = 0
        self.dummy_center_y = 0
        self.dummy_flag = False
        self.dummy_count = 0
        #  end

        self.angle = 0
        self.frequent = 5.0  # 视频帧检测频率。
        self.track_time = 1.0 / self.frequent
        self.k = 0

        self.cascade_model = None
        self.select_classifier_model()

        self.font = cv.InitFont(cv.CV_FONT_HERSHEY_DUPLEX, 1, 1, 0, 1, 8)

        self.video = None
        self.stop_thread_flag = False

        # enum
        # (face_default, face_alt) = (0, 1)

    def __del__(self):
        """
        Function: End Process VideoCapture()
        :return:
        """
        if self.video is None:
            return
        self.video.release()
        cv2.destroyAllWindows()

    # take control of the camera
    def open_camera(self):
        camera_num = 1
        # t = threading.Thread(target=self.open_ffmpeg)
        # t.daemon = True
        # t.start()
        self.video = cv2.VideoCapture(camera_num)
        # self.video = cv2.VideoCapture("outpipe")
        self.video.set(3, 640)
        self.video.set(4, 480)

    # release the control of camera
    def release_camera(self):
        self.video.release()
        cv2.destroyAllWindows()

    # select model for different purpose
    def select_classifier_model(self, path=None):
        if path is None:
            path = "/usr/local/share/OpenCV/haarcascades/haarcascade_frontalface_default.xml"
        else:
            path = "/usr/local/share/OpenCV/haarcascades/" + path + ".xml"
        self.cascade_model = None
        self.cascade_model = cv2.CascadeClassifier(path)

    def face_detection(self, face=True):
        # print "video status: ", self.video.isOpened()
        if self.video is None or not self.video.isOpened():
            self.open_camera()

        while not self.stop_thread_flag:
            if self.count == len(self.file_names):
                self.count = 0
            success, self.frame = self.video.read()
            cv2.waitKey(10)
            if face is True:
                if self.count_time % self.frequent == 0:
                    # detect faces by calling opencv
                    self.faces = self._frame_cascade(self.frame)
                    self.face_position = []

                    # can't find a face
                    if len(self.faces) == 0:
                        self.count_time -= 1
                        self._position_track(0, 0, False)
                        self.dummy_flag = False
                    # only one face is detected
                    elif len(self.faces) == 1:
                        self.face_position = self.faces
                        center_x = self.face_position[0][0] + int(self.face_position[0][2] / 2)
                        center_y = self.face_position[0][1] + int(self.face_position[0][3] / 2)
                        if not self.dummy_flag:
                            self.dummy_center_x = self.face_position[0][0] + int(self.face_position[0][2] / 2)
                            self.dummy_center_y = self.face_position[0][1] + int(self.face_position[0][3] / 2)
                            self.dummy_flag = True
                        else:
                            if abs(self.dummy_center_x - center_x) < 20 and \
                                    abs(self.dummy_center_y - center_y) < 20:
                                self.dummy_center_x = center_x
                                self.dummy_center_y = center_y
                                self._position_track(self.face_position[0][0], self.face_position[0][2], True)
                                self._face_verify()
                        # self.dummy_count += 1
                        # if self.dummy_count == 5:
                        #     self.dummy_count = 0
                        #     self.dummy_flag = False
                    # multiple faces exist
                    else:
                        self.face_position = self.faces
                        self._face_verify()
                        dis = self._distance_detect(self.face_position)

                else:
                    dis = self._distance_detect(self.face_position)

            self.count_time += 1

            cv2.imshow('video', self.frame)
        self.release_camera()

    def face_detection_web(self, face=True):
        if self.video is None:
            self.open_camera()

        if self.count == len(self.file_names):
            self.count = 0
        success, self.frame = self.video.read()
        cv2.waitKey(50)
        if face is True:
            if self.count_time % self.frequent == 0:
                self.faces = self._frame_cascade(self.frame)
                self.face_position = []

                # can't find a face
                if len(self.faces) == 0:
                    self.count_time -= 1
                    self._position_track(0, 0, False)
                    self.dummy_flag = False
                # only one face is detected
                elif len(self.faces) == 1:
                    self.face_position = self.faces
                    center_x = self.face_position[0][0] + int(self.face_position[0][2] / 2)
                    center_y = self.face_position[0][1] + int(self.face_position[0][3] / 2)
                    if not self.dummy_flag:
                        self.dummy_center_x = self.face_position[0][0] + int(self.face_position[0][2] / 2)
                        self.dummy_center_y = self.face_position[0][1] + int(self.face_position[0][3] / 2)
                        self.dummy_flag = True
                    else:
                        if abs(self.dummy_center_x - center_x) < 20 and \
                                abs(self.dummy_center_y - center_y) < 20:
                            self.dummy_center_x = center_x
                            self.dummy_center_y = center_y
                            self._position_track(self.face_position[0][0], self.face_position[0][2], True)
                            self._face_verify()
                    # self.dummy_count += 1
                    # if self.dummy_count == 5:
                    #     self.dummy_count = 0
                    #     self.dummy_flag = False
                # multiple faces exist
                else:
                    self.face_position = self.faces
                    self._face_verify()
                    dis = self._distance_detect(self.face_position)

            else:
                dis = self._distance_detect(self.face_position)

        self.count_time += 1
        ret, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tostring()

    def _frame_cascade(self, cas_frame):
        gray = cv2.cvtColor(cas_frame, cv2.COLOR_BGR2GRAY)
        frame_cascade = self.cascade_model.detectMultiScale(
            gray, scaleFactor=1.3, minNeighbors=4, minSize=(30, 30), flags=cv2.cv.CV_HAAR_SCALE_IMAGE)
        # cv2.cv.CV_HAAR_FEATURE_MAX
        return frame_cascade

    def _face_verify(self):
        cv2.imwrite(self.file_names[self.count], self.frame)
        if self.count_time == 40:
            t = threading.Thread(target=self._verify)
            t.daemon = True
            t.start()

            self.remember_age_gender_result, self.remember_person_name_warn_result, self.face_center_x,\
                self.face_center_y = self.static_recognize(self.res, self.detect)
            if len(self.remember_age_gender_result) >= 2:
                # deal with voice match on people
                if self.flag_voice_many_people == 0:
                    self.flag_else = False
                    self.flag_voice_many_people += 1
                    t1 = threading.Thread(target=self.pv.say_baidu("大家好！"))
                    t1.daemon = True
                    t1.start()
            self.count_time = 0
        self.count += 1

    def _distance_detect(self, faces, PutText=False):
        dis = 0
        for i in range(0, len(faces)):
            x = faces[i][0]
            y = faces[i][1]
            w = faces[i][2]
            h = faces[i][3]
            self.cv_center_x = x + int(w / 2)
            self.cv_center_y = y + int(h / 2)
            # distance hacked!!!!
            distance = 100 / w + 0.2
            dis = float('%0.2f' % distance)
            if PutText is False:
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                self._put_text(faces[i], dis)
        return dis

    def _verify(self):
        self.res, self.detect = self.fpp.verify_multiple_people(img_file=self.file_names[self.count])

    @staticmethod
    def static_recognize(res, detect):
        age = []
        gender = []
        person_age_and_gender = []
        person_name = []
        center_x = []
        center_y = []
        if detect is not None:
            for i in range(0, len(detect['face'])):
                age.append(str(detect['face'][i]['attribute']['age']['value']))
                gender.append(" " + str(detect['face'][i]['attribute']['gender']['value']))
                cx = detect['face'][i]['position']['center']['x']
                img_width = detect['img_width']
                center_x.append(int(cx * img_width / 100))
                cy = detect['face'][i]['position']['center']['y']
                img_height = detect['img_height']
                center_y.append(int(cy * img_height / 100))
        if res is not None:
            for i in range(0, len(res)):
                person_name.append(res[i])
        for i in range(0, len(age)):
            person_age_and_gender.append(age[i] + gender[i])
        return person_age_and_gender, person_name, center_x, center_y

    def _put_text(self, face, dis):
        x = face[0]
        y = face[1]
        h = face[3]
        if len(self.remember_age_gender_result) > 0:
            text_to_video_dis_and_age_and_gender = str(dis) + "m "
            cv.PutText(cv.fromarray(self.frame), text_to_video_dis_and_age_and_gender,
                       (x-2, y-2), self.font, (255, 0, 0))

            for i in range(0, len(self.face_center_x)):
                if abs(self.cv_center_x-self.face_center_x[i]) < 20 and \
                                abs(self.cv_center_y-self.face_center_y[i]) < 20:

                    text_to_video_dis_and_age_and_gender = str(dis) + "m " + self.remember_age_gender_result[i]
                    text_to_video_name_or_warn = self.remember_person_name_warn_result[i]
                    # deal with voice match on people
                    # self._voice_match_people(text_to_video_name_or_warn)
                    cv.PutText(cv.fromarray(self.frame), text_to_video_dis_and_age_and_gender, (x-2, y-2),
                               self.font, (255, 0, 0))
                    y = y + h + 20
                    cv.PutText(cv.fromarray(self.frame), text_to_video_name_or_warn,
                               (x, y), self.font, (255, 0, 0))
                    self.distances[self.file_names[self.count-1]] = dis
                    break
        else:
            text_to_video_dis_and_age_and_gender = str(dis) + "m "
            text_to_video_name_or_warn = "waiting..."
            cv.PutText(cv.fromarray(self.frame), text_to_video_dis_and_age_and_gender,
                       (x-2, y-2), self.font, (255, 0, 0))
            y = y + h + 20
            cv.PutText(cv.fromarray(self.frame), text_to_video_name_or_warn, (x, y), self.font, (255, 0, 0))
            self.distances[self.file_names[self.count-1]] = dis

    def _position_track(self, x, w, is_people):
        """
        :param x:
        :param w:
        :return: move speed & position angle
        """
        DEFAULT_DIS = 0.7
        STAY_AREA = 0.15
        self.command_flag = False
        if is_people is False:
            speed = 0
            angle = 0
            self.data_flag = True
            self.wheel_stop()
            return speed, angle
        # 实际距离（m） = （像素距离 *2.54  / 分辨率 ）ps:目前我们的图片分辨率为96dpi,位深度24.像素为640*480
        # 此算法存在争议，后期会深入更改
        pixel_dis = float('%0.2f' % (2.54 * abs(x + w / 2 - self.x - self.w / 2) / 96))
        speed = float('%0.2f' % (pixel_dis / self.track_time))
        # print 'Move Speed is : %0.2f m/s.' % speed
        self.x = x
        self.w = w
        angle = int((math.atan(((x + w / 2) - 320) / 1024) * 180 / math.pi))   # -left + right

        # calculate relative angle
        if angle > 5:
            self.wheel_turnright()

        elif angle < -5:
            self.wheel_turnleft()
        else:
            self.data_flag = True
            # calculate relative distance
            dis = self._distance_detect(self.face_position, True)
            # decide to move forward or backward or just stop
            # forward
            if dis > DEFAULT_DIS + STAY_AREA:
                # print "wait for me"
                self.wheel_forward()
            # backward
            elif dis < DEFAULT_DIS - STAY_AREA/2:
                # print "stay back!!!"
                self.wheel_backward()
            # stop
            else:
                self.wheel_stop()

        # print(angle)
        print "angle %d" % angle
        # print 'Move Speed is : %0.2f m/s.' % speed

        return speed, angle

    def _voice_match_people(self, text_to_video_name_or_warn):

        if self.flag_voice_one_people_l == 0 and text_to_video_name_or_warn == "L. Honghua":
            self.flag_voice_one_people_l += 1
            t2 = threading.Thread(target=self.pv.say_baidu("你好呀，刘红华"))
            t2.daemon = True
            t2.start()
        if self.flag_voice_one_people_y == 0 and text_to_video_name_or_warn == "Y. Shuai":
            self.flag_voice_one_people_y += 1
            t3 = threading.Thread(target=self.pv.say_baidu("你好呀，严帅"))
            t3.daemon = True
            t3.start()
        if text_to_video_name_or_warn == "not in db" and self.flag_voice_one_people_unknown == 0:
            self.flag_voice_one_people_unknown += 1
            t4 = threading.Thread(target=self.pv.say_baidu("你好啊，我好像不认识你呀。"))
            t4.daemon = True
            t4.start()

    def stop_thread(self):
        self.stop_thread_flag = True

    def start_thread(self):
        self.stop_thread_flag = False

    def open_ffmpeg(self, flag=True):
        os.system("ffmpeg -f video4linux2 -i /dev/video0 -f mpeg1video -s 320x240  -b:v 64k -r 30 "
                  "http://123.57.176.245:8082/123/320/240/ -f avi -s 640x480 -r 10 -y pipe:1 > outpipe")

if __name__ == '__main__':
    fd = FaceDetect()
    fd.face_detection()