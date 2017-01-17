# coding=utf-8
from __future__ import division
import threading
import math
import os

import cv2

import cv2.cv as cv

import gui.fpp_lib as fpp
from voice import PyVoice as pv
import library.vision.Track.PythonCallMatlab as PCM
import vision.Track.FaceDirection_client as FDC


class VisionOnline(object):
    def __init__(self):
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

        self.face_direction_flag = False  # if you want to test face direction, you should set face_direction_flag TRUE
        self.pcm = PCM.PythonCallMatlab()
        self.fdc = None

        self.flag_voice_many_people = 0
        self.flag_voice_one_people_l = 0
        self.flag_voice_one_people_y = 0
        self.flag_voice_one_people_unknown = 0
        self.flag_else = True
        self.x = 0
        self.w = 0
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

        # t = threading.Thread(target=self.open_ffmpeg)
        # t.daemon = True
        # t.start()
        self.video = cv2.VideoCapture(1)
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
        self.cascade_model = cv2.CascadeClassifier(path)

    def face_detection(self, face=True):
        if self.video is None or not self.video.isOpened():
            self.open_camera()
        if self.face_direction_flag:
            # face direction
            t = threading.Thread(target=self.pcm.run_connect)  # start matlab server
            t.daemon = True
            t.start()
            while True:
                try:
                    self.fdc = FDC.FDClient()  # start python client
                    break
                except:
                    pass
        while not self.stop_thread_flag:
            if self.count == len(self.file_names):
                self.count = 0
            success, self.frame = self.video.read()

            cv2.waitKey(50)
            if face is True:
                if self.count_time % self.frequent == 0:
                    # detect faces by calling opencv
                    # time1 = time.time()
                    self.faces = self._frame_cascade(self.frame)
                    # time2 = time.time()
                    # print "time for cascade detect: ",time2-time1
                    self.face_position = []

                    # can't find a face
                    if len(self.faces) == 0:
                        self.count_time -= 1
                        if self.face_direction_flag:
                            face_angle, position = self.call_mat(self.frame)
                            if face_angle != -1:
                                distance_return, face_dis = self.face_distance_mat(position)
                                self.draw_face_direction(self.frame, position, None, face_dis)
                                print "angle is:", face_angle
                            else:
                                pass
                    # only one face is detected
                    elif len(self.faces) == 1:
                        self.face_position = self.faces
                        self._position_track(self.face_position[0][0], self.face_position[0][2], True)
                        self._face_verify()
                    # multiple faces exist
                    else:
                        self.face_position = self.faces
                        self._face_verify()
                        self._distance_detect(self.face_position)

                else:
                    self._distance_detect(self.face_position)

            self.count_time += 1

            cv2.imshow('video', self.frame)
        self.release_camera()
        self.fdc.fd_client('2')

    def _frame_cascade(self, cas_frame):
        gray = cv2.cvtColor(cas_frame, cv2.COLOR_BGR2GRAY)
        frame_cascade = self.cascade_model.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30), flags=cv2.cv.CV_HAAR_FEATURE_MAX)
        return frame_cascade

    def _face_verify(self):
        cv2.imwrite(self.file_names[self.count], self.frame)
        if self.count_time == 40:
            t = threading.Thread(target=self._verify)
            t.daemon = True
            t.start()

            self.remember_age_gender_result, self.remember_person_name_warn_result, self.face_center_x,\
                self.face_center_y = self.recognize(self.res, self.detect)
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
            # print distance
            if PutText is False:
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (255, 0, 0), 1)
                self._put_text(faces[i], dis)
        return dis

    def face_distance_mat(self, position):
        width = float(position[2] - position[0])
        distance = 100 / width + 0.2
        dis = float('%0.2f' % distance)
        dis_meter = str(dis)+"m"
        return dis, dis_meter

    def draw_face_direction(self, dst, (x0, y0, x1, y1), txt=None, distance=None):
        # draw name
        if txt is not None:
            cv2.putText(dst, txt, (x0-20, y0-20), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 0), lineType=cv2.CV_AA)
        # draw distance
        if distance is not None:
            cv2.putText(dst, distance, (x0-20, y0), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 0, 0), lineType=cv2.CV_AA)
        # Draw the face area in image:
        cv2.rectangle(dst, (x0, y0), (x1, y1), (255, 0, 0), 1)
        # cv2.waitKey(10)

    def _verify(self):
        self.res, self.detect = self.fpp.verify_multiple_people(img_file=self.file_names[self.count])

    def recognize(self, res, detect):
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

    def _position_track(self, x, w, is_people, mat_index=None):
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
            # self.wheel_stop()
            return speed, angle
        # 实际距离（m） = （像素距离 *2.54  / 分辨率 ）ps:目前我们的图片分辨率为96dpi,位深度24.像素为640*480
        # 此算法存在争议，后期会深入更改
        pixel_dis = float('%0.2f' % (2.54 * abs(x + w / 2 - self.x - self.w / 2) / 96))
        speed = float('%0.2f' % (pixel_dis / self.track_time))
        # print 'Move Speed is : %0.2f m/s.' % speed
        self.x = x
        self.w = w
        angle = 0
        if mat_index is None:
            angle = int((math.atan(((x + w / 2) - 320) / 1024) * 180 / math.pi))   # -left + right
        else:
            angle = mat_index
        # calculate relative angle
        if angle > 5:
            # self.wheel_turnright()
            pass
        elif angle < -5:
            pass
            # self.wheel_turnleft()
        else:
            pass
            # self.wheel_stop()
            # self.data_flag = True
            # # calculate relative distance
            # dis = self._distance_detect(self.face_position, True)
            # # decide to move forward or backward or just stop
            # # forward
            # if dis > DEFAULT_DIS + STAY_AREA:
            #     # print "wait for me"
            #     self.wheel_forward()
            # # backward
            # elif dis < DEFAULT_DIS - STAY_AREA/2:
            #     # print "stay back!!!"
            #     self.wheel_backward()
            # # stop
            # else:
            #     self.wheel_stop()
        # print(angle)
        print "angle %d" % angle
        # print 'Move Speed is : %0.2f m/s.' % speed
        return speed, angle

    def stop_thread(self):
        self.stop_thread_flag = True

    def start_thread(self):
        self.stop_thread_flag = False

    def call_mat(self, frame):
        im = cv2.resize(frame, (133, 100))  # resize for matlab face direction
        path = os.getcwd()
        path_ai_flag = False  # if through AI run, the path_ai_flag should set TRUE
        if not path_ai_flag:
            path = os.path.dirname(path)
            path = os.path.dirname(path)
        file_fd = path + "/facedirection/fd.jpg"
        cv2.imwrite(file_fd, im)
        mat_return = self.fdc.fd_client('1')
        mat_angle, position = self.convert_data(mat_return)
        return mat_angle, position

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
                        round(float(mat_return[2])))-112
            ori_x0 = int(100 * round(float(mat_return[5])) + 10 * round(float(mat_return[6])) +
                         round(float(mat_return[7])))-112
            ori_y0 = int(100 * round(float(mat_return[10])) + 10 * round(float(mat_return[11])) +
                         round(float(mat_return[12])))-112
            ori_x1 = int(100 * round(float(mat_return[15])) + 10 * round(float(mat_return[16])) +
                         round(float(mat_return[17])))-112
            ori_y1 = int(100 * round(float(mat_return[20])) + 10 * round(float(mat_return[21])) +
                         round(float(mat_return[22])))-112
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


if __name__ == '__main__':
    vo = VisionOnline()
    vo.face_detection()