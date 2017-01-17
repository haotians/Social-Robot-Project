
# this class is used to control motion
import threading
import time

import motion_control.ArmControlClassForMX
import library.motion_control.WheelControlClass


class MotionControl(object):

    def __init__(self):
        # object names of other modules
        self.arm_target = None
        self.wheel_target = None
        self.sensor_listener_target = None
        # object for calculation
        self.arm_control_class = motion_control.ArmControlClassForMX.ArmControlClassForMX()
        self.wheel_control_class = library.motion_control.WheelControlClass.WheelControlClass()
        # a thread to listen several sensors
        self.thread_running_flag = False  # a flag used to stop 'thread_temp'
        self.thread_temp = None  # a thread
        # commands from ui or vision
        self.arm_command = None
        self.wheel_command = None
        self.command_flag = False

    def __del__(self):
        self.stop_thread()

    def get_command(self, flag, arm_command, wheel_command):
        self.command_flag = flag
        self.arm_command = arm_command
        self.wheel_command = wheel_command

    def start_thread(self):
        # start thread
        self.thread_temp = threading.Thread(target=self.motion_control_main)
        self.thread_temp.daemon = True  # daemon means the child thread will quit when main thread quit
        self.thread_running_flag = True  # used to stop thread
        self.thread_temp.start()  # start thread

    def stop_thread(self):
        # stop thread
        self.thread_running_flag = False

    def set_arm_target(self, target):
        self.arm_target = target
        self.arm_control_class.serial_transmit_object = target

    def set_wheel_target(self, target):
        self.wheel_target = target
        self.wheel_control_class.serial_transmit_object = target

    def set_sensor_listener_target(self, target):
        self.sensor_listener_target = target

    def motion_control_main(self):
        while self.thread_running_flag:

            # execute arm command
            if self.arm_command is not None:
                if self.arm_target is not None:
                    self.arm_control_class.create_control_data(self.arm_command)
                self.arm_command = None

            # execute wheel command
            if self.wheel_command is not None:
                if self.wheel_target is not None:
                    self.wheel_control_class.create_control_data(self.wheel_command)
                self.wheel_command = None

            time.sleep(0.01)

