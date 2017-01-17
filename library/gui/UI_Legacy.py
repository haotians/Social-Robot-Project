# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-03-01


# command line interface
def execute_cmd(self, *args):
    data = args[0]
    print "cmd command: ", data
    if data == "obj":
        self._obj_detect()
    elif data == "camon":
        commands = []
        commands.append(self.message_object.message_warp('control_data', 2))
        commands.append(self.message_object.message_warp("vision", 'cam_on'))
        self.output_all_messages(commands)
        self.output_status_to_master(False)
    elif data == 'camoff':
        data = 'cam_off'
        # warp data and send it topic and master
        commands = []
        commands.append(self.message_object.message_warp("control_data", 5))
        commands.append(self.message_object.message_warp('no_command', 0))
        # commands = self.message_object.message_warp("vision", data)
        # self.output_message_to_topic()
        self.output_all_messages(commands)
        print('Camera OFF')
    elif data == 'stoptrain':
        commands = []
        commands.append(self.message_object.message_warp("control_data", 2))
        commands.append(self.message_object.message_warp('no_command', 0))
        self.output_all_messages(commands)
        print('stop training')
    elif data == 'track':
        commands = []
        commands.append(self.message_object.message_warp("control_data", 23))
        commands.append(self.message_object.message_warp('no_command', 0))
        self.output_all_messages(commands)

    elif data == 'point':
        commands = []
        data = [1]
        commands.append(self.message_object.message_warp('for_marker', data))
        self.output_all_messages(commands)

    elif data == 'roam':
        commands = []
        commands.append(self.message_object.message_warp("control_data", 24))
        commands.append(self.message_object.message_warp('no_command', 0))
        self.output_all_messages(commands)

    elif data == 'cloud':
        commands = []
        commands.append(self.message_object.message_warp("control_data", 27))
        commands.append(self.message_object.message_warp('no_command', 0))
        self.output_all_messages(commands)


def _obj_detect(self):
    print "obj_detect"
    data = 100
    commands = [self.message_object.message_warp("control_data", data, "ui")]
    self.output_all_messages(commands)


def _stop_obj_detect(self):
    print "obj_detect stops"
    data = 101
    commands = [self.message_object.message_warp("control_data", data, "ui")]
    self.output_all_messages(commands)

# if __name__ == '__main__':
#     robot_ui = RobotControl(None)
#     SERVER = "127.0.0.1"
#     PORT = 28426
#
#     socketIO_test = SocketIO(SERVER, PORT, lognamespace)
#
#     socketIO_test.on('Head_H', robot_ui.head_component)
#     socketIO_test.on('Head', robot_ui.head_control)
#
#     socketIO_test.on('armXY', robot_ui.arm_component)
#     socketIO_test.on('armZ', robot_ui.arm_component)
#     socketIO_test.on('armBI', robot_ui.arm_component)
#     socketIO_test.on('record', robot_ui.arm_component)
#     socketIO_test.on('Music', robot_ui.arm_component)
#     socketIO_test.on('Hand', robot_ui.arm_component)
#
#     socketIO_test.on('reset', robot_ui.reset_control)
#     socketIO_test.on('move', robot_ui.on_move)
#     socketIO_test.on('movtarget', robot_ui.move_target)
#     socketIO_test.on('stop', robot_ui.button_stop)
#
#     socketIO_test.on('cam', robot_ui.video_component)
#
#     socketIO_test.on('aud', robot_ui.voice_component)
#     socketIO_test.on('listen', robot_ui.voice_component)
#
#     socketIO_test.on('Roaming', robot_ui.app_component)
#     socketIO_test.on('FaceTrack', robot_ui.app_component)
#     socketIO_test.on('ObjRecognize', robot_ui.app_component)
#     socketIO_test.on('EmotionDetect', robot_ui.app_component)
#     socketIO_test.on('Marker', robot_ui.app_component)
#     socketIO_test.on('name', robot_ui.app_component)  # train face recognition (advise change another name)
#     # socketIO_test.on('botcmd', robot_ui.execute_cmd)
#     socketIO_test.wait()
#
#
# if __name__ == '__main__':
#     master = Components.Master()
#     ui = RobotControl(master)
#     ui.port = 80
#     ui.server = '123.57.176.245'
#     ui._node_run()
#     print ui.cam_stream_port