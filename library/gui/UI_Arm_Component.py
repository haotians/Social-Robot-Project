# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-19
from library.vision.AI_models.arm_ai import *


def arm_response(master, command):
    print command
    if cmp(command, 'W') == 0:
        button_arm_upward(master)
    elif cmp(command, 'A') == 0:
        button_arm_turn_left(master)
    elif cmp(command, 'S') == 0:
        button_arm_downward(master)
    elif cmp(command, 'D') == 0:
        button_arm_turn_right(master)
    elif cmp(command, 'CLOSE') == 0:
        button_arm_close(master)
    elif cmp(command, 'OPEN') == 0:
        button_arm_open(master)
    elif cmp(command, 'arm_6') == 0:
        point_marker(master)
    elif cmp(command, 'arm_1') == 0:
        arm_1(master)
    elif cmp(command, 'arm_2') == 0:
        arm_2(master)
    elif cmp(command, 'arm_3') == 0:
        arm_3(master)
    elif cmp(command, 'arm_4') == 0:
        arm_4(master)
    elif cmp(command, 'arm_5') == 0:
        arm_5(master)
    elif cmp(command, 'In') == 0:
        arm_control_z_forward(master)
    elif cmp(command, 'Out') == 0:
        arm_control_z_inward(master)
    elif cmp(command, 'START') == 0:  # record start (advise change another name)
        record_on(master)
    elif cmp(command, 'STOP') == 0:  # record stop(advise change another name)(when after click A W D S, ui return STOP)
        record_off(master)
    elif cmp(command, 'PlayRecord') == 0:
        button_arm_play_record(master)
    elif cmp(command, 'Left') == 0:
        hand_left(master)
    elif cmp(command, 'Right') == 0:
        hand_right(master)
    elif cmp(command, 'Both') == 0:
        hand_both(master)
    elif cmp(command[0:6], 'Music:') == 0:
        music_control(master, command)
    elif cmp(command, 'RESET') == 0:
        reset_on(master)


def button_arm_upward(master):
    data = arm_cartesian_move("up")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm upward'


def button_arm_turn_left(master):
    data = arm_cartesian_move("left")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm turn left'


def button_arm_downward(master):
    data = arm_cartesian_move("down")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm downward'


def button_arm_turn_right(master):
    data = arm_cartesian_move("right")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm turn right'


def button_arm_close(master):
    data = arm_close_work()
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm close'


def button_arm_open(master):
    data = arm_open_work()
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm open'


def point_marker(master):
    data = [1]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("for_marker", data, "ui")]
    master.output_all_messages(commands)
    print "point_to_marker"


def arm_1(master):
    data = [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm_predefined_1'


def arm_2(master):
    data = [2, './data/arm_trajectory/back_wave', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm_predefined_2'


def arm_3(master):
    data = [2, './data/arm_trajectory/finger_point', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm_predefined_3'


def arm_4(master):
    data = [18, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'music_initial'


def arm_5(master):
    data = [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm_default_pid'


def arm_control_z_forward(master):
    data = arm_cartesian_move("in")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm forward'


def arm_control_z_inward(master):
    data = arm_cartesian_move("out")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'arm inward'


def record_on(master):
    data = arm_record_trajectory()
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Record Start'


def record_off(master):
    data = arm_end_record_trajectory()
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Record Stop'


def button_arm_play_record(master):
    data = [2, './data/arm_trajectory/a_word', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'play record'


def hand_left(master):
    data = arm_status("left")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'left hand'


def hand_right(master):
    data = arm_status("right")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'right hand'


def hand_both(master):
    data = arm_status("both")
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'both hands'


def music_control(master, command):
    music_name = str(command)
    data = arm_move_music(music_name)
    # warp data and send it topic and master
    voice_data = '...'
    if cmp(music_name, 'Music:Music_1') == 0:
        voice_data = '我给你弹一首童话吧'
    if cmp(music_name, 'Music:Music_2') == 0:
        voice_data = '我给你弹一首找朋友,注意听欧'
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    commands.append(master.message_object.message_warp('voice_data', voice_data))
    master.output_all_messages(commands)
    print 'music control'


def reset_on(master):
    print 'arm reset'

