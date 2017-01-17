# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-19


def wheel_response(master, command):
    print command


def on_move(master, command):
    angle = command["movAngle"]
    speed = command["movSpeed"]
    # generate data
    data = [0, speed, angle, 0]
    # print "UI", data
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("wheel_data", data, "ui")]
    master.output_all_messages(commands)
    print 'on move'


def move_target(master, command):
    print(command["x"], command["y"])
    x = command["x"]
    y = command["y"]
    # generate data
    data = [x, y]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("wheel_command", data, "ui")]
    master.output_all_messages(commands)
    print 'move target'


def button_stop(master):
    data = [0, 0, 0, 0]
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("wheel_data", data, "ui")]
    master.output_all_messages(commands)
    print 'wheel stop'




