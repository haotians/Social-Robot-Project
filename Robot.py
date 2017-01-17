# Author: everyone, Last Modified Date: 2016-02-17
# Author: Yehang Liu, Last Modified Date: 2016-02-18
# Author: Honghua Liu, Last Modified Date: 2016-03-02
import time
import copy

from components import Components
import DecisionTree as DT
import library.voice.Voice as voice
import library.gui.UIControl as UI
import library.vision.Vision.Vision as vision
import application.TrainFaceRecognition as tfr
import application.DefaultControl as defaultcontrol
import library.vision.CameraSupport.CameraControl as CameraControl
import library.motion_control.SensorListener as SensorListener
import library.motion_control.SerialTransmit as SerialTransmit
import library.motion_control.WheelNode as WheelNode
import library.motion_control.NewArmNode as ArmNode
import application.MarkerAPI as MarkerAPI
from library.vision.CameraSupport.CameraControl import open_camera
import application.PersonTrack as PersonTrack
import application.ObjectRecognition as obj_detect
import application.Roam as Roam
import application.PersonTrackToCloud as Cloud
import application.EmotionDetect as emotion_detection
import robot_startup.robotconfig as RobotConfig


class Robot(Components.Master):
    def __init__(self):
        Components.Master.__init__(self)
        self.dt_node = None
        # web UI definition
        self.port_ui = 80
        self.server_ui = '123.57.176.245'

        # allocation robot id, must be globally unique
        self.robot_id = 3

        # initial camera
        self.camera = CameraControl.CameraControl()
        self.camera_occupy = None
        self.cap = None

    def create_a_node(self, node_type):
        # type list:
        #
        # sensor_listener
        # serial_transmit
        # wheel_node
        # arm_node
        # voice_node
        # dt_node
        # UI_node
        # app_train_face
        # vision_node

        # ddd
        a_object = None
        if node_type is 'sensor_listener':
            a_object = SensorListener.SensorListener(self)
        elif node_type is 'serial_transmit':
            a_object = SerialTransmit.SerialTransmit(self)
        elif node_type is 'wheel_node':
            a_object = WheelNode.WheelNode(self)
        elif node_type is 'arm_node':
            a_object = ArmNode.ArmNode(self)
        elif node_type is 'voice_sys':
            a_object = voice.Voice(self)
        elif node_type is 'dt_sys':
            a_object = DT.DecisionTree(self)
            self.dt_node = a_object
        elif node_type is 'UI_sys':
            a_object = UI.RobotControl(self)
        elif node_type is 'app_train_face':
            self.cap = open_camera(self.cap)
            a_object = tfr.TrainFaceRecognition(self, self.cap)
        elif node_type is 'vision_sys':
            self.cap = open_camera(self.cap)
            a_object = vision.Vision(self, self.cap)
        elif node_type is 'default_control':
            a_object = defaultcontrol.DefaultControl(self)
        elif node_type is 'marker_sys':
            self.cap = open_camera(self.cap, [1280, 720])
            a_object = MarkerAPI.Marker(self, self.cap)
        elif node_type is 'face_track':
            a_object = PersonTrack.PersonTrack(self)
        elif node_type is 'roam':
            a_object = Roam.Roam(self)
        elif node_type is 'cloud':
            a_object = Cloud.PersonTrackToCloud(self)
        elif node_type is 'object_detect':
            self.cap = open_camera(self.cap)
            a_object = obj_detect.ObjectRecognition(self, self.cap)
        elif node_type is 'emotion_detect':
            self.cap = open_camera(self.cap)
            a_object = emotion_detection.EmotionDetection(self, self.cap)
        return a_object

    def _process_control_data(self, status):

        if 0 < status <= 10:
            self._camera_control(status)
        # voice
        elif 10 < status <= 20:
            self._voice_control(status)
        elif status is 23:
            RobotConfig.start_track(self)
        elif status is 24:
            RobotConfig.stop_track(self)
        elif status is 25:
            RobotConfig.start_test_roam(self)
        elif status is 26:
            RobotConfig.stop_test_roam(self)
        elif status is 27:
            RobotConfig.start_cloud(self)
        # else
        # ......
        #library/gui/UIControl.py

    def _camera_control(self, mode):
        print "camera mode: ", mode
        if mode == 0:
            return
        # release camera

        self.kill_current_vision_system(mode)

        # stop pipe
        # self.camera.stop_camera()
        time.sleep(0.02)
        # then preform the tasks
        # local vision system is on

        self.camera_occupy = mode
        print self.camera_occupy

        if mode == 2:
            RobotConfig.start_vision_system(self)

        # web cam now is open
        if mode == 3:
            self.camera.update_camera(True, mode, None)
            self.camera.run_camera()

        if mode == 5:
            RobotConfig.start_marker_detection(self)

        if mode == 6:
            RobotConfig.start_emotion_detection(self)

        if mode == 7:
            RobotConfig.start_train_new_person_system(self)

        if mode == 8:
            RobotConfig.start_object_detection(self)

        self.dt_node.set_master_confirmation_status(True)

    def kill_current_vision_system(self, mode):
        if self.camera_occupy is not None and self.camera_occupy != mode:
            if self.camera_occupy is 2:
                RobotConfig.stop_vision_sys(self)
            elif self.camera_occupy is 3:
                self.camera.stop_camera()
            elif self.camera_occupy is 5:
                RobotConfig.stop_marker_detection(self)
            elif self.camera_occupy is 6:
                RobotConfig.stop_emotion_detection(self)
            elif self.camera_occupy is 7:
                RobotConfig.stop_train_new_person_system(self)
            elif self.camera_occupy is 8:
                RobotConfig.stop_object_detection(self)
            if self.cap is not None:
                self.cap.release()

    def _voice_control(self, mode):
        if mode == 11:
            self.change_node_confirmation_target('voice_node')
            RobotConfig.stop_voice_system(self)
        # baidu method
        elif mode == 12:
            useBaidu = True
            self.change_node_confirmation_target('voice_node')
            RobotConfig.start_voice_system(self, useBaidu)
        # xunfei method
        elif mode == 13:
            print "method called for local voice"
            useBaidu = False
            self.change_node_confirmation_target('voice_node')
            RobotConfig.start_voice_system(self, useBaidu)

    # read node report, make according changes to nodes or topics when control_data is detected
    def check_node_status(self):
        # check status loop
        while True:
            time.sleep(0.01)
            # define control_data must be transmitted from DT, one msg each loop
            control_data = None
            # sleep a little bit
            time.sleep(self.node_check_time)
            length_node_active = len(self.all_nodes_name)
            # loop all the active nodes to get there
            node_check_list = copy.copy(self.node_check_list_buffer)
            # successfully delete the node
            if self.node_check_name is not None and \
                            self.all_nodes_name.count(self.node_check_name) == 0:
                self.node_check_name = None
                self.dt_node.set_master_confirmation_status(True)

            for i in range(length_node_active):
                status = node_check_list[i]
                # node failed
                if status < 0:
                    # print "failed to read data from node: ",self.active_nodes_id[i]
                    # todo: restart the node
                    pass
                # node working, do nothing
                elif status == 0:
                    # successfully active the node
                    if self.all_nodes[i].name == self.node_check_name:
                        self.node_check_name = None
                        self.dt_node.set_master_confirmation_status(True)
                    continue

                # AI node working and it pass the control_data to master
                else:
                    # erase data
                    self.node_check_list_buffer[i] = 0
                    print "master find control_data in node: ", self.all_nodes[i].name
                    control_data = status

            # print "active Node: ", self.active_nodes_id
            # process control_data
            if control_data is None:
                continue
            else:
                self._process_control_data(control_data)
                # self._control_data_list(control_data)

    def init_system(self):
        # initialize decision tree
        self.add_node('dt_sys', 'dt_node')
        RobotConfig.start_ui_system(self)
        RobotConfig.start_voice_system(self, False)
        RobotConfig.start_default_control_system(self)
        # RobotConfig.start_wheel(self)
        # RobotConfig.start_wheel(self)
        # RobotConfig.start_arm(self)

if __name__ == '__main__':
    robot_sys = Robot()
    robot_sys.init_system()
    robot_sys.check_node_status()



