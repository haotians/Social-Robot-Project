# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-03-02
import time
from socketIO_client import SocketIO
from socketIO_client import LoggingNamespace as Log_Namespace
import components.Components as Components
import UI_Arm_Component as UAC
import UI_App_Component as UPC
import UI_Video_Component as UVDC
import UI_Voice_Component as UVIC
import UI_Wheel_Component as UWC
import UI_Head_Component as UHC
import threading


class RobotControl(Components.Node):
    def __init__(self, master_object):
        # init father
        Components.Node.__init__(self, master_object)
        self.server = None
        self.port = None
        self.robot_id = None
        self.feedback_thread = None
        self.feedback_thread_flag = False
        self.socket_IO = None
        self.cam_stream_port = None

    def set_node_status(self, info):
        self.server = info[0]
        self.port = info[1]
        self.robot_id = info[2]

    def _node_run(self):
        print 'UI started'
        self.start_ui()
        while 1:
            time.sleep(0.1)
            # 1. check topics
            # 2. process
            # 3. report
            pass

    def start_ui(self):
        try:
            self.socket_IO = SocketIO(self.server, self.port, Namespace)
        except:
            print "failed to init socketIO"
            return
        self.socket_IO.emit('botonline', {'id': self.robot_id, 'msg': 'bot is online'})

        self.socket_IO.on('Head_H', self.head_component)
        self.socket_IO.on('Head', self.head_control)

        self.socket_IO.on('armXY', self.arm_component)
        self.socket_IO.on('armZ', self.arm_component)
        self.socket_IO.on('armBI', self.arm_component)
        self.socket_IO.on('record', self.arm_component)
        self.socket_IO.on('Hand', self.arm_component)
        self.socket_IO.on('Music', self.arm_component)
        self.socket_IO.on('reset', self.arm_component)

        self.socket_IO.on('move', self.on_move)
        self.socket_IO.on('movtarget', self.move_target)
        self.socket_IO.on('stop', self.button_stop)

        self.socket_IO.on('cam', self.video_component)

        self.socket_IO.on('aud', self.voice_component)
        self.socket_IO.on('listen', self.voice_component)

        self.socket_IO.on('Roaming', self.app_component)
        self.socket_IO.on('FaceTrack', self.app_component)
        self.socket_IO.on('ObjRecognize', self.app_component)
        self.socket_IO.on('EmotionDetect', self.app_component)
        self.socket_IO.on('Marker', self.app_component)
        self.socket_IO.on('name', self.app_component)  # train face recognition (advise change another name)
        # socketIO.on('botcmd', self.execute_cmd)
        self.socket_IO.on('streamport', self.on_server_reply)
        # start sub-thread
        self.start_ui_feedback()
        self.socket_IO.wait()

    def on_server_reply(self, *args):
        if args[0]:
            self.cam_stream_port = str(args[0])

    # head component start
    def head_component(self, *args):
        UHC.head_response(self, args[0])

    def head_control(self, *args):
        UHC.head_control(self, args[0])
    # end

    def arm_component(self, *args):
        UAC.arm_response(self, args[0])

    # wheel component start
    def on_move(self, *args):
        UWC.on_move(self, args[0])

    def move_target(self, *args):
        UWC.move_target(self, args[0])

    def button_stop(self, *args):
        UWC.button_stop(self)
    # end

    def app_component(self, *args):
        UPC.app_response(self, args[0])

    def video_component(self, *args):
        UVDC.video_response(self, args[0])

    def voice_component(self, *args):
        UVIC.voice_response(self, args[0])

    # sub-thread of UI thread to feed back status of Robot
    def start_ui_feedback(self):
        self.feedback_thread = threading.Thread(target=self.ui_feedback)
        self.feedback_thread.daemon = True
        self.feedback_thread_flag = True
        self.feedback_thread.start()

    def ui_feedback(self):
        while self.feedback_thread_flag:

            if self.thread_active is False:
                break

            messages = self.get_messages_from_all_topics()

            self.process_messages(messages)

            time.sleep(0.01)

    def process_messages(self, messages):
        for i in range(len(messages)):
            if messages[i] is not None:
                time_marker, msg_type, data, msg_source = self.message_object.message_dewarp(messages[i])
                if msg_type is 41:
                    self.socket_transmit(data, msg_source)

    def socket_transmit(self, data, msg_source):
        if cmp(self.message_object._generate_source_type_id(msg_source), 'sensor_listener') == 0:
            self.socket_IO.emit('message', {'id': self.robot_id, 'data': data})


class Namespace(Log_Namespace):
    def on_connect(self):
        print('[Connected]')