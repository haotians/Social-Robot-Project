# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-19


def voice_response(master, command):
    print command
    if cmp(command, 'ONWeb') == 0:
        aud_on_web(master)
    elif cmp(command, 'ONLocal') == 0:
        aud_on_local(master)
    elif cmp(command, 'OFF') == 0:
        aud_off(master)
    elif cmp(command, 'listenOn') == 0:
        listen_on(master)
    elif cmp(command, 'listenOff') == 0:
        listen_off(master)


def aud_on_web(master):
    data = 12
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("control_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Audio ON Web'


def aud_on_local(master):
    data = 13
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("control_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Audio ON Local'


def aud_off(master):
    data = 11
    # warp data and send it topic and master
    commands = [master.message_object.message_warp("control_data", data, "ui")]
    master.output_all_messages(commands)
    print 'Audio OFF'


def listen_on(master):
    data = 0
    commands = [master.message_object.message_warp("listen_on_off", data, "ui")]
    master.output_all_messages(commands)
    print 'Listen ON'


def listen_off(master):
    data = 1
    commands = [master.message_object.message_warp("listen_on_off", data, "ui")]
    master.output_all_messages(commands)
    print 'Listen OFF'


