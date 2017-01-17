# Author: Yehang Liu, Last Modified data: 2016-02-18

# Contains the startup function for threads works for Apps

import time
import robotconfig

# config of adding new person


def start_train_new_person_system(master):
    # init node

    master.camera.stop_camera()
    master.change_node_confirmation_target('tf_node')
    master.add_node('app_train_face', 'tf_node', None, ['voice_data', 'control_data'])

    # init Train New Person topic

    master.add_topic('topic_dt2tf', ['train_face'])
    master.add_topic('topic_tf2dt', ['voice_data', 'control_data'])
    master.add_topic('topic_tf2arm', ['arm_command'])

    # link nodes to topic

    master.link_node_topic('dt_node', 'topic_dt2tf', 'output_of_node')
    master.link_node_topic('tf_node', 'topic_dt2tf', 'input_of_node')
    master.link_node_topic('dt_node', 'topic_tf2dt', 'input_of_node')
    master.link_node_topic('tf_node', 'topic_tf2dt', 'output_of_node')
    master.link_node_topic('tf_node', 'topic_tf2arm', 'output_of_node')
    master.link_node_topic('arm_node', 'topic_tf2arm', 'input_of_node')


def stop_train_new_person_system(master):
    print 'stop train_new_person'
    # delete node
    # master.camera.stop_camera()
    master.change_node_confirmation_target('tf_node')
    master.del_node('tf_node')
    master.del_topic('topic_dt2tf')
    master.del_topic('topic_tf2dt')
    master.del_topic('topic_tf2arm')


# config of roaming system

def start_test_roam(master):

    master.change_node_confirmation_target('roam_node')
    master.add_node('roam', 'roam_node', None)

    # topic from wheel node to roam
    master.add_topic('topic_wheel2roam', ['wheel_move_stage'])
    master.link_node_topic('roam_node', 'topic_wheel2roam', 'input_of_node')
    master.link_node_topic('wheel_control', 'topic_wheel2roam', 'output_of_node')

    # topic roam to wheel node
    master.add_topic('topic_roam2wheel', ['wheel_command'])
    master.link_node_topic('roam_node', 'topic_roam2wheel', 'output_of_node')
    master.link_node_topic('wheel_control', 'topic_roam2wheel', 'input_of_node')

    # topic for speak
    master.add_topic('topic_roam2voice', ['voice_data'])
    master.link_node_topic('roam_node', 'topic_roam2voice', 'output_of_node')
    master.link_node_topic('voice_node', 'topic_roam2voice', 'input_of_node')

    # topic sensor to roam
    master.add_topic('topic_sensor2roam', ['robot_position', 'sonar_distance'])
    master.link_node_topic('sensor_listener', 'topic_sensor2roam', 'output_of_node')
    master.link_node_topic('roam_node', 'topic_sensor2roam', 'input_of_node')


def stop_test_roam(master):
    print 'stop test_roam'
    # delete node
    # master.thread_active = False
    master.change_node_confirmation_target('roam_node')
    master.del_node('roam_node')
    master.del_topic('topic_roam2wheel')
    master.del_topic('topic_wheel2roam')
    master.del_topic('topic_sensor2roam')


# config of tracking function

def start_track(master):

    if 'vision_node' not in master.all_nodes_name:
        master.kill_current_vision_system(2)
        robotconfig.start_vision_system(master)
        time.sleep(3)
        master.camera_occupy = 2

    master.change_node_confirmation_target('track_node')

    master.add_node('face_track', 'track_node', None, ['wheel_command'])

    # topic track to wheel node
    master.add_topic('topic_track2wheel', ['wheel_command'])
    master.link_node_topic('track_node', 'topic_track2wheel', 'output_of_node')
    master.link_node_topic('wheel_control', 'topic_track2wheel', 'input_of_node')

    # topic sensor to track
    master.add_topic('topic_sensor2track', ['robot_position'])
    master.link_node_topic('sensor_listener', 'topic_sensor2track', 'output_of_node')
    master.link_node_topic('track_node', 'topic_sensor2track', 'input_of_node')

    # topic from wheel node to track
    master.add_topic('topic_wheel2track', ['wheel_move_stage'])
    master.link_node_topic('track_node', 'topic_wheel2track', 'input_of_node')
    master.link_node_topic('wheel_control', 'topic_wheel2track', 'output_of_node')


def stop_track(master):
    master.change_node_confirmation_target('track_node')
    master.del_node('track_node')
    master.del_topic('topic_track2wheel')
    master.del_topic('topic_sensor2track')
    master.del_topic('topic_wheel2track')


# config of marker detection

def start_marker_detection(master):
    master.camera.stop_camera()
    master.change_node_confirmation_target('marker_node')
    master.add_node('marker_sys', 'marker_node', None, ['arm_command'])

    master.add_topic('marker_node_to_arm_node', ['arm_command'])
    master.link_node_topic('marker_node', 'marker_node_to_arm_node', 'output_of_node')
    master.link_node_topic('arm_control', 'marker_node_to_arm_node', 'input_of_node')

    master.add_topic('marker_node_to_voice_node', ['voice_data'])
    master.link_node_topic('marker_node', 'marker_node_to_voice_node', 'output_of_node')
    master.link_node_topic('voice_node', 'marker_node_to_voice_node', 'input_of_node')

    master.add_topic('dt_node_to_marker_node', ["for_marker"])
    master.link_node_topic('dt_node', 'dt_node_to_marker_node', 'output_of_node')
    master.link_node_topic('marker_node', 'dt_node_to_marker_node', 'input_of_node')


def stop_marker_detection(master):
    print "stop marker detection"
    master.change_node_confirmation_target('marker_node')
    master.del_node('marker_node')
    master.del_topic('marker_node_to_arm_node')
    master.del_topic('marker_node_to_voice_node')
    master.del_topic('dt_node_to_marker_node')


# config of emotion detection

def start_emotion_detection(master):
    master.change_node_confirmation_target('emotion_node')

    master.add_node('emotion_detect', 'emotion_node', None)

    master.add_topic('emotion2voice',['voice_data'])
    master.link_node_topic('emotion_node', 'emotion2voice', 'output_of_node')
    master.link_node_topic('voice_node', 'emotion2voice', 'input_of_node')


def stop_emotion_detection(master):
    master.change_node_confirmation_target('emotion_node')
    master.del_node('emotion_node')
    master.del_topic('emotion2voice')


# config of object recognition

def start_object_detection(master):
    master.change_node_confirmation_target('node_obj_detect')

    master.add_node('object_detect', 'node_obj_detect')

    master.add_topic('topic_obj2voice', ["voice_data"])

    master.link_node_topic('node_obj_detect', 'topic_obj2voice', 'output_of_node')
    master.link_node_topic('voice_node', 'topic_obj2voice', 'input_of_node')


def stop_object_detection(master):
    print "stop object recognition"
    master.change_node_confirmation_target('node_obj_detect')
    master.del_node('node_obj_detect')
    master.del_topic('topic_obj2voice')