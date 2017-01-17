# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-19
from library.vision.AI_models.arm_ai import *


def head_response(master, command):
    print command
    if cmp(command, 'Head_Down') == 0:
        head_downs(master)
    elif cmp(command, 'Head_Up') == 0:
        head_up(master)


def head_downs(master):
    data = [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Head down'


def head_up(master):
    data = [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0]
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Head up'


def head_control(master, command):
    xy = int(command["xy"])
    z = int(command["z"])
    data = head_move(xy, z)
    commands = [master.message_object.message_warp("arm_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Head control'

