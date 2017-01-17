# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-03-01


def video_response(master, command):
    print command
    if cmp(command, 'ONWeb') == 0:
        cam_on_web(master)
    elif cmp(command, 'ONLocal') == 0:
        cam_on_local(master)
    elif cmp(command, 'ON') == 0:
        ui_vision_on(master)
    elif cmp(command, 'OFF') == 0:
        cam_off(master)


def cam_on_web(master):
    data = 3
    cam_stream_port = master.cam_stream_port
    # warp data and send it topic and master
    commands = []
    master.master.camera.update_camera(False, 1, cam_stream_port)
    commands.append(master.message_object.message_warp("control_data", data, "ui"))
    master.output_all_messages(commands)
    master.output_status_to_master(False)
    print 'Cam ON Web'


def cam_on_local(master):
    commands = []
    commands.append(master.message_object.message_warp('control_data', 2, 'ui'))
    master.output_all_messages(commands)
    master.output_status_to_master(False)
    print 'Cam ON Local'


def ui_vision_on(master):
    data = 'cam_on'
    data_control =3
    # warp data and send it topic and master
    commands = []
    commands.append(master.message_object.message_warp('control_data', data_control))
    commands.append(master.message_object.message_warp("vision", data))
    master.output_all_messages(commands)
    master.output_status_to_master(False)
    print 'Camera ON'


def cam_off(master):
    data_control = 1
    # warp data and send it topic and master
    commands = []
    commands.append(master.message_object.message_warp("control_data", data_control))
    commands.append(master.message_object.message_warp('no_command', 0))
    master.output_all_messages(commands)
    master.output_status_to_master(False)
    print 'Camera OFF'



