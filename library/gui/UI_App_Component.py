# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-19
import unicodedata


def app_response(master, command):
    print command
    if cmp(command, 'Roaming') == 0:
        roaming_start(master)
    elif cmp(command, 'StopRoaming') == 0:
        roaming_stop(master)
    elif cmp(command, 'FaceTrack') == 0:
        track_start(master)
    elif cmp(command, 'StopFaceTrack') == 0:
        track_stop(master)
    elif cmp(command, 'ObjRecognize') == 0:
        obj_recognize(master)
    elif cmp(command, 'StopObjRecognize') == 0:
        obj_recognize_stop(master)
    elif cmp(command, 'EmotionDetect') == 0:
        emotion_detect(master)
    elif cmp(command, 'StopEmotionDetect') == 0:
        emotion_detect_stop(master)
    elif cmp(command, 'Marker') == 0:
        marker_recognition(master)
    elif cmp(command, 'StopMarker') == 0:
        marker_recognition_stop(master)
    elif cmp(command, 'DetectMarker') == 0:
        marker_detect(master)
    elif cmp(command[0:5], 'name:') == 0:  # train face recognition (advise change another name)
        train_face_recognition(master, command)


def roaming_start(master):
    print 'Roaming start'
    data = 25
    commands = []
    commands.append(master.message_object.message_warp("control_data", data, "ui"))
    commands.append(master.message_object.message_warp('control_data', 2))
    master.output_all_messages(commands)


def roaming_stop(master):
    print 'Roaming stop'
    data = 26
    commands = []
    commands.append(master.message_object.message_warp("control_data", data, "ui"))
    commands.append(master.message_object.message_warp('control_data', 5))
    data_stop_wheel = [0, 0, 0, 0]
    # warp data and send it topic and master
    commands.append(master.message_object.message_warp("wheel_data", data_stop_wheel))
    master.output_all_messages(commands)


def track_start(master):
    print 'Track start'
    data = 23
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def track_stop(master):
    print 'Track Stop'
    data = 24
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def obj_recognize(master):
    print 'start object recognition'
    data = 8
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def obj_recognize_stop(master):
    print 'stop object recognition'
    data = 1
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def emotion_detect(master):
    print 'start emotion detect'
    data = 6
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def emotion_detect_stop(master):
    print 'stop emotion detect'
    data = 1
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def marker_recognition(master):
    print 'start marker recognition'
    data = 5
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def marker_recognition_stop(master):
    print 'stop marker recognition'
    data = 1
    commands = [master.message_object.message_warp('control_data', data)]
    master.output_all_messages(commands)


def marker_detect(master):
    print 'Detect Marker start'
    data = 1
    commands = [master.message_object.message_warp('for_marker', data)]
    master.output_all_messages(commands)


def train_face_recognition(master, command):
    print 'train face recognition'
    # unicode to UTF-8
    commands = []
    data = unicodedata.normalize('NFKD', command[5:]).encode('UTF-8')
    # warp data and send it topic and master
    commands.append(master.message_object.message_warp("train_face", [2, data], "ui"))
    commands.append(master.message_object.message_warp('control_data', 7))
    master.output_all_messages(commands)
