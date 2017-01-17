# Author: Yehang Liu, Last Modified data: 2016-02-18
# Author: Honghua Liu, Last Modified Date: 2016-03-02 add robot_id
# Contains the startup function for threads that starts with Robot

import serial
from robot_startup.robotconfigApp import *


# config of UI


def start_ui_system(master):
    ui_info = [master.server_ui, master.port_ui, master.robot_id]
    # initialize UI system
    master.add_node('UI_sys', 'UI_node', ui_info)
    # init UI topic
    master.add_topic('topic_ui2dt', ["arm_data", "wheel_data", "control_data", "train_face",
                                     'vision', "for_marker", "listen_on_off",'voice_data'])
    # link nodes to topic
    master.link_node_topic('UI_node', 'topic_ui2dt', 'output_of_node')
    master.link_node_topic('dt_node', 'topic_ui2dt', 'input_of_node')


# config of voice system

def start_voice_system(master, useBaidu):

    master.add_node('voice_sys', 'voice_node', useBaidu)
    master.add_topic('topic_voice2dt', ['voice_command', 'control_data', "confirmation",
                                        'train_face', 'wheel_data', 'arm_data'])
    master.add_topic('topic_dt2voice', ['voice_data', 'listen_on_off'])
    # link nodes to topic
    master.link_node_topic('voice_node', 'topic_voice2dt', 'output_of_node')
    master.link_node_topic('dt_node', 'topic_voice2dt', 'input_of_node')
    master.link_node_topic('voice_node', 'topic_dt2voice', 'input_of_node')
    master.link_node_topic('dt_node', 'topic_dt2voice', 'output_of_node')


def stop_voice_system(master):
    master.del_node('voice_node')


# config of default control system

def start_default_control_system(master):
    # init node
    master.add_node('default_control', 'dc_node', None, ['arm_data', 'wheel_data', 'voice_command'])
    # init Default Control topic
    master.add_topic('topic_dt2dc', ['arm_data', 'wheel_data', 'voice_command'])
    # link nodes to topic
    master.link_node_topic('dt_node', 'topic_dt2dc', 'output_of_node')
    master.link_node_topic('dc_node', 'topic_dt2dc', 'input_of_node')


# config of vision system

def start_vision_system(master):
    # init node
    # master.camera.stop_camera()
    master.change_node_confirmation_target('vision_node')
    master.add_node('vision_sys', 'vision_node', None, ['voice_data', 'control_data', 'wheel_command'])
    # init Train Vision to Decision Tree topic
    master.add_topic('topic_dt2vision', ['vision'])
    master.add_topic('topic_vision2dt', ['voice_data', 'control_data'])
    # link nodes to topic
    master.link_node_topic('dt_node', 'topic_dt2vision', 'output_of_node')
    master.link_node_topic('vision_node', 'topic_dt2vision', 'input_of_node')

    master.link_node_topic('dt_node', 'topic_vision2dt', 'input_of_node')
    master.link_node_topic('vision_node', 'topic_vision2dt', 'output_of_node')


def stop_vision_sys(master):
    master.camera.stop_camera()
    master.change_node_confirmation_target('vision_node')
    # delete node
    master.del_node('vision_node')
    master.del_topic('topic_vision2dt')
    master.del_topic('topic_vision2wheel')
    master.del_topic('topic_dt2vision')


# config of wheel system

def start_wheel(master):
    ser_wheel = serial.Serial("/dev/arduino021", baudrate=115200, timeout=None)
    # ser_wheel = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=None)
    master.add_node('serial_transmit', 'wheel_serial', [ser_wheel, 8, 14, "wheel_imu_sonar"])
    master.add_topic('topic_wheel_to_serial', ['wheel_to_serial'])

    # link nodes to topic

    master.link_node_topic('wheel_serial', 'topic_wheel_to_serial', 'input_of_node')

    master.add_node('wheel_node', 'wheel_control')

    # link nodes to topic

    master.link_node_topic('wheel_control', 'topic_wheel_to_serial', 'output_of_node')

    # link to dt

    master.add_topic('topic_dc_to_wheel', ['wheel_command'])
    master.link_node_topic('wheel_control', 'topic_dc_to_wheel', 'input_of_node')
    master.link_node_topic('dc_node', 'topic_dc_to_wheel', 'output_of_node')

    # add sensor

    master.add_node('sensor_listener', 'sensor_listener')
    master.add_topic('topic_wheel_serial_to_sensor_listener', ['wheel_imu_sonar'])
    master.link_node_topic('sensor_listener', 'topic_wheel_serial_to_sensor_listener', 'input_of_node')
    master.link_node_topic('wheel_serial', 'topic_wheel_serial_to_sensor_listener', 'output_of_node')

    # Link sensor listener to UI

    master.add_topic('topic_sensor_to_UI', ['position_on_UI'])
    master.link_node_topic('sensor_listener', 'topic_sensor_to_UI', 'output_of_node')
    master.link_node_topic('UI_node', 'topic_sensor_to_UI', 'input_of_node')

    # topic sensor to wheel node

    master.add_topic('topic_sensor_listener_to_wheel_node', ['robot_position'])
    master.link_node_topic('wheel_control', 'topic_sensor_listener_to_wheel_node', 'input_of_node')
    master.link_node_topic('sensor_listener', 'topic_sensor_listener_to_wheel_node', 'output_of_node')


# config of cloud-deck system

def start_cloud(master):
    master.add_node('cloud', 'cloud_node', None)


# config of arm system

def start_arm(master):
    # ser_arm = serial.Serial("/dev/arduino011", baudrate=115200, timeout=None)
    ser_arm = serial.Serial("/dev/arduino011", baudrate=115200, timeout=None)
    master.add_node('serial_transmit', 'arm_serial', [ser_arm, 21, 20, "arm_head"])
    master.add_topic('topic_arm_to_serial', ['arm_to_serial'])
    # link nodes to topic
    master.link_node_topic('arm_serial', 'topic_arm_to_serial', 'input_of_node')

    master.add_node('arm_node', 'arm_control')
    # link nodes to topic
    master.link_node_topic('arm_control', 'topic_arm_to_serial', 'output_of_node')
    # link to default control
    master.add_topic('topic_dc_to_arm', ['arm_command'])
    master.link_node_topic('arm_control', 'topic_dc_to_arm', 'input_of_node')
    master.link_node_topic('dc_node', 'topic_dc_to_arm', 'output_of_node')

    master.add_topic('arm_serial_to_arm_control', ['arm_head'])
    master.link_node_topic('arm_control', 'arm_serial_to_arm_control', 'input_of_node')
    master.link_node_topic('arm_serial', 'arm_serial_to_arm_control', 'output_of_node')

