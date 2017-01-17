# coding=utf-8
import time
import threading
import sys
import os

reload(sys)
sys.setdefaultencoding( "utf-8" )

import legacy.MotionControl
from library import motion_control
import library.motion_control.SensorListener
import library.voice.PyVoice as pv
import library.gui.ewaybot as webui
from library.vision.Vision import Vision as vision_alt
from library.vision.CameraSupport import CameraControl


class Core(object):

    def __init__(self):
        # serial port definition
        self.wheel_ser = None
        self.arm_ser = None
        self.imu_and_sonar_ser = None

        # self.wheel_ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=None)
        # self.arm_ser = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=None)
        # self.imu_and_sonar_ser = serial.Serial("/dev/ttyACM1", baudrate=115200, timeout=None)

        # initial serial transmit
        self.wheel_transmit = motion_control.SerialTransmitForMX.SerialTransmitForMX()
        self.arm_transmit = motion_control.SerialTransmitForMX.SerialTransmitForMX()
        self.imu_and_sonar_transmit = motion_control.SerialTransmitForMX.SerialTransmitForMX()

        # initial motion system
        self.motion_control = legacy.MotionControl.MotionControl()
        # initial sensor listener
        self.sensor_listener = library.motion_control.SensorListener.SensorListener()


        # web UI definition
        self.port_ui = 80
        self.server_ui = '123.57.176.245'

        # initial vision system
        # self.vision = cd.FaceDetect()
        self.vision = vision_alt.Vision()

        # initial voice system
        self.voice = pv.EWayVoice()

        # initial UI
        self.ui = webui.RobotControl()

        # initial camera
        self.camera = CameraControl.CameraControl()

        # active system # vision voice UI arms wheels
        self.active_systems = [0, 0, 0, 0, 0]

        # initial cv_web
        # self.cvweb = cv_web.

        # listen flag
        self.listen_flag = True

        # Data source number: voice vision and UI
        self.num_sources = 3

        # Data sources objects
        # self.data_sources = [self.Vision,self.voice,self.UI]

        # Data sources threads
        self.t_listen = None
        self.t_vision = None
        self.t_ui = None
        self.t_voice = None
        self.threads = []

        self.file_check()

    def __del__(self):
        self.kill_all_system()

    # check the pipe file
    def file_check(self):
        if os.path.exists("outpipe"):
            return
        else:
            os.system("mkfifo outpipe")

    # check hardware system initialization
    def system_check(self):
        # motion_control.status_check is not available now
        if not self.motion_control.status_check():
            return False

        # leave room for future add_in components like depth camera, SLAM
        return True

    # start all command system
    def start_all_command_system(self):

        self.start_ui_system()
        self.start_local_vision_system()
        self.start_voice_system()

    def start_local_vision_system(self):

        self.vision.start_thread()
        # self.camera.update_camera(True,2,"nan")
        # self.camera.run_camera()
        self.t_vision = threading.Thread(target=self.vision.face_detection)
        self.t_vision.daemon = True
        self.t_vision.start()
        self.active_systems[0] = 1

        print "Vision system started "

    def start_ui_system(self):

        # kill local vision system, MUST BE MODIFIED!!!
        # self.kill_local_vision_system()
        self.t_ui = threading.Thread(target=self.ui.start_ui_system, args=(self.server_ui, self.port_ui, ))
        self.t_ui.daemon = True
        self.t_ui.start()

        print "UI system started "
        self.active_systems[2] = 1

    def start_voice_system(self, useBaidu = True):
        self.voice.update_voice_method(useBaidu)
        self.t_voice = threading.Thread(target=self.voice.voice_detect)
        self.t_voice.daemon = True
        self.t_voice.start()
        self.active_systems[1] = 1

    def start_listen(self):
        self.listen_flag = True
        self.t_listen = threading.Thread(target=self._listen_command)
        # self.t_listen.daemon = True
        self.t_listen.start()

    def start_mechanical_system(self):
        # link sensor listener and motion control
        self.motion_control.set_sensor_listener_target(self.sensor_listener)

        # start wheel system
        if self.wheel_ser is None:
            print "Unable to start wheels"
        else:
            # build up links between instances
            self.wheel_transmit._ser = self.wheel_ser
            self.wheel_transmit.servo_num = 2

            self.sensor_listener.wheel_target = self.wheel_transmit
            self.motion_control.set_wheel_target(self.wheel_transmit)
            # start wheel transmit thread
            self.wheel_transmit.start_thread()

        # start arm system
        if self.arm_ser is None:
            print "Unable to start arms"
        else:
            # build up links between instances
            self.arm_transmit._ser = self.arm_ser
            self.arm_transmit.servo_num = 8

            self.sensor_listener.arm_target = self.arm_transmit
            self.motion_control.set_arm_target(self.arm_transmit)
            # start arm transmit thread
            self.arm_transmit.start_thread()

        # start imu and sonar system
        if self.imu_and_sonar_ser is None:
            print "Unable to start imu and sonar"
        else:
            # build up links between instances
            self.imu_and_sonar_transmit._ser = self.imu_and_sonar_ser
            self.imu_and_sonar_transmit.servo_num = 8

            self.sensor_listener.imu_and_sonar_target = self.imu_and_sonar_transmit
            # start arm transmit thread
            self.imu_and_sonar_transmit.start_thread()

        # start motion control thread and sensor listener thread
        self.motion_control.start_thread()
        self.sensor_listener.start_thread()

    def kill_all_system(self):
        if self.active_systems[0] == 1:
            self.kill_local_vision_system()
        if self.active_systems[1] == 1:
            self.kill_voice_system()
        if self.active_systems[2] == 1:
            self.kill_ui_system()
        self.kill_mechanical_system()
        self.stop_listen()

    def kill_voice_system(self):
        self.voice.stop_thread()
        self.active_systems[1] = 0
        print "voice system is killed"

    def kill_local_vision_system(self):
        self.vision.stop_thread()
        self.active_systems[0] = 0
        print "local vision system is killed"

    def kill_ui_system(self):
        self.active_systems[2] = 0
        print "UI system is killed"

    def kill_mechanical_system(self):
        self.motion_control.stop_thread()
        self.sensor_listener.stop_thread()
        self.imu_and_sonar_transmit.stop_thread()
        self.wheel_transmit.stop_thread()
        self.arm_transmit.stop_thread()
        print "whole mechanical system is killed"

    # main loop for listening command from voice, vision and UI
    def _listen_command(self):

        while self.listen_flag:
            # loop over the sources and determine which command to take
            flag = False
            data_wheels = None
            data_arms = None

            flag, data_wheels, data_arms = self._simple_decision(flag, data_wheels, data_arms)

            # print "flag:", flag, "data_a:", data_arms, "data_w:", data_wheels
            # print "active system: ", self.active_systems

            loop_command = True

            # give command to motion control
            self.motion_control.get_command(loop_command, data_arms, data_wheels)

            # sleep a little bit
            self.__listen_time()
        print "quit listen"

    # simple AI: when command comes, the AI output command by priority UI>voice>vision
    def _simple_decision(self, flag, data_wheels, data_arms):

        flag_vision = flag_voice = flag_ui = False
        data_wheels_vision = data_wheels_voice = data_wheels_ui = None
        data_arms_vision = data_arms_voice = data_arms_ui = None

        for source in range(self.num_sources):
            # print "enter for source loop: ", source
            # 0: vision 1:voice 2: UI
            if self.active_systems[source] == 0:
                continue
            if source == 0:
                # print "source:0 entered"
                flag_vision, data_wheels_vision, data_arms_vision, data_cloud_deck, data_control_vision = self.vision.output_command()
                # print "data_w from vision: ", data_wheels_vision
                # self.vision.clean_command_arms()
                self.vision.clean_command_wheels()

            if source == 1:
                # get signal
                flag_voice, data_wheels_voice, data_arms_voice, data_cloud_deck, data_control_voice = self.voice.output_command()
                #
                if flag_voice:
                    self._process_control_data(self.voice, data_control_voice)
                    self.voice.clean_command_arms()
                    self.voice.clean_command_wheels()

            if source == 2:
                flag_ui, data_wheels_ui, data_arms_ui, data_cloud_deck, data_control_ui = self.ui.output_command()

                # print "flag:", flag_ui, "data_a:", data_arms_ui, "data_w:", data_wheels_ui
                if flag_ui:
                    # print "source:2 entered"
                    # if data_control_ui == 2:
                    #     self.start_local_vision_system()
                    #     self.ui.clean_data_control()
                    # elif data_control_ui == 1:
                    #     self.kill_local_vision_system()
                    #     self.ui.clean_data_control()
                    # print "ui data in core: ", data_control_ui
                    # print "ui wheel in core:", data_wheels_ui
                    # self.vision.stop_thread()
                    self._process_control_data(self.ui, data_control_ui)
                    self.ui.clean_command_arms()

        # First priority UI
        if flag_ui:
            return flag_ui, data_wheels_ui, data_arms_ui
        # second priority voice
        elif not flag_ui and flag_voice:
            return flag_voice, data_wheels_voice, data_arms_voice
        # third priority vision
        elif not flag_ui and not flag_voice and flag_vision:
            return flag_vision, data_wheels_vision, data_arms_vision
        # have no command
        else:
            return flag, data_wheels, data_arms

    # stop listening command
    def stop_listen(self):
        self.listen_flag = False
        print "stop listen"

    def __listen_time(self, sleep_time = 0.02):
        # sleep 20ms for the system
        time.sleep(sleep_time)
        # if times > 10000:
        #     # self.stop_listen()
        #     # self.voice.say("I spent too much time outside")
        # pass

    # process control data and perform according tasks
    def _process_control_data(self, target, mode):
        # camera
        if mode == 0:
            return

        if mode <= 10 and mode > 0:
            self._camera_control(mode)
        # voice
        elif mode <= 20 and mode >10:
            self._voice_control(mode)
        # else
        # ......
        #
        target.clean_data_control()

    def _camera_control(self, mode):
        print "camera mode: ", mode
        if mode == 0:
            return
        # release camera first
        self.kill_local_vision_system()
        self.camera.stop_camera()
        time.sleep(0.02)
        # then preform the tasks

        if mode == 2 :
            self.camera.update_camera(True, mode, None)
            self.vision.source_camera()
            self.start_local_vision_system()

        if mode == 4:
            self.camera.update_camera(True, mode, None)
            self.vision.source_pipe()
            # self.camera.run_camera()
            self.start_local_vision_system()
            self.camera.run_camera()

        elif mode == 3:
            self.camera.update_camera(True, mode, None)
            self.camera.run_camera()
            self.active_systems[0] = 1

        elif mode == 5:
            # use camera for tarining
            self.vision.source_camera()
            # add new person
            self.vision.add_new_person("lol")
            # open camera
            self.start_local_vision_system()

    def _voice_control(self, mode):
        if mode == 11:
            self.kill_voice_system()
        # baidu method
        elif mode == 12:
            useBaidu = True
            self.start_voice_system(useBaidu)
        # xunfei method
        elif mode == 13:
            useBaidu = False
            self.start_voice_system(useBaidu)

    def check_status(self):
        # thread check_in and system status check
        pass

if __name__ == '__main__':

    core_object = Core()
    # core_object.voice.say("1")
    # if core_object.system_check():
    # core_object.start_mechanical_system()
    # core_object.start_ui_system()
    # core_object.start_voice_system(False)
    # core_object.voice.say_xunfei('举头望明月，低头思故乡')
    # core_object.voice.say_baidu('Please raise your head')
    core_object.start_local_vision_system()
    # core_object.start_ui_system()
    # core_object.vision.add_new_person("Filon")
    # time.sleep(5)
    # core_object.vision.stop_thread()
    # core_object.start_voice_system()
    core_object.start_listen()
    # core_object._listen_command()
    # # if the system initialization
    # if 1>0 :
    #
    #     core_object.start_mechanical_system()
    #     # core_object.start_local_vision_system()
    #     core_object.start_ui_system()
    #     core_object.start_listen()
    #     # core_object.kill_mechanical_system()
