# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-17
import time
import components.Components as Components
import math
import random
from scipy import constants

sleep_time = 2


class Roam(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)

        self.stop_flag = False
        self.sleep_time = 0.05

        self.sonar_threshold = 20

    def get_sensor_data(self):
        robot_position = None
        sonar_data = None
        move_stage = None
        # read msg from topics, ie imu data fro this app
        messages = self.get_messages_from_all_topics()
        # read sensor data
        for one_message in messages:

            if one_message[1] == 71:
                time_marker, message_type, robot_position, source = self.message_object.message_dewarp(one_message)
                # print 'position', robot_position
                # print 'position message received'
            elif one_message[1] == 72:
                time_marker, message_type, sonar_data, source = self.message_object.message_dewarp(one_message)
                # print 'sonar message received'
            elif one_message[1] == 83:
                time_marker, message_type, move_stage, source = self.message_object.message_dewarp(one_message)
                # print 'move stage message received'
            else:
                continue
        return robot_position, sonar_data, move_stage

    def angle_protection(self, angle):

        if angle > math.pi:
            angle += -2 * math.pi
        elif angle < -math.pi:
            angle += 2 * math.pi
        return angle

    def random_set_goal(self, robot_position, sonar_data):
        radius = 2

        current_x = robot_position[0]
        current_y = robot_position[1]
        current_theta = robot_position[2]
        # rotation_angle increment
        # random_angle = -math.pi + random.random() * 2 * math.pi
        random_angle = self.rotation_angle(sonar_data)
        # new target angle
        target_angle = current_theta + random_angle
        target_angle = self.angle_protection(target_angle)

        raw_command = [current_x + radius * math.cos(target_angle),
                       current_y + radius * math.sin(target_angle),
                       target_angle]

        # print "goal", raw_command
        # print "current", robot_position

        return raw_command

    def check_position(self, current_position, target_position):

        XY_couple_tolerance = 0.15
        theta_tolerance = 0.05

        error = None
        if target_position is not None:
            error = [target_position[0]-current_position[0],
                     target_position[1]-current_position[1],
                     target_position[2]-current_position[2]]

        # if target_position is None, indicates that it's the first loop, step 0 is next
        else:
            return True

        # angle protection
        error[2] = self.angle_protection(error[2])

        # print "target_position: ", target_position
        # print "current position: ", current_position

        # check error, return true if tolerance is reached
        # print "error x: ", error[0]
        # print "error y: ", error[1]
        # print "error theta: ", error[2]

        # check position
        if (abs(error[0]) + abs(error[1]) ) < XY_couple_tolerance and abs(error[2]) < theta_tolerance:
            time.sleep(0.5)
            return True
        else:
            return False

    def process_message(self, command):
        msg = list()
        raw_message = [3] + command
        msg.append(self.message_object.message_warp('wheel_command', raw_message))
        self.output_all_messages(msg)

    def _node_run(self):
        # target_pos

        time.sleep(sleep_time)
        print 'roam started'

        msg_voice = []
        msg_voice.append(self.message_object.message_warp('voice_data', '让我来巡逻保护你吧'))
        self.output_all_messages(msg_voice)

        while self.thread_active:

            # report to master
            self.output_status_to_master(False)

            # get current position
            robot_position, sonar_data, move_stage = self.get_sensor_data()
            # sensor protection
            # todo: this condition requires the cycle of 'Roam' significantly slower than 'WheelNode' and 'Sensor...'
            # todo: maybe need to modify
            if robot_position is None or sonar_data is None or move_stage is None:
                time.sleep(self.sleep_time)
                continue

            # check position and return stage id
            sonar_interrupt = self.check_sonar_status(sonar_data, move_stage)

            # status check
            if sonar_interrupt is True and move_stage >= 2:
                print 'obstacle detected, stop wheel action'
                msg_out = list()
                msg_out.append(self.message_object.message_warp('wheel_command', [1, 0, 0, 0]))
                self.output_all_messages(msg_out)
                time.sleep(1)

            elif move_stage == 0:
                target_position = self.random_set_goal(robot_position, sonar_data)
                self.process_message(target_position)
                print 'generate a random goal', target_position

            else:
                print "target position is not reached, continue looping..."

            time.sleep(self.sleep_time)

        # msg_out = list()
        # msg_out.append(self.message_object.message_warp('wheel_command', [1, 0, 0, 0]))
        # self.output_all_messages(msg_out)
        print "finish roaming"

        msg_voice = []
        msg_voice.append(self.message_object.message_warp('voice_data', '巡逻结束，我要休息一下'))
        self.output_all_messages(msg_voice)


    def check_sonar_status(self, sonar_data, move_stage):
        if min(sonar_data) <= self.sonar_threshold:

            interrupt = True
        else:
            interrupt = False
        return interrupt

    def rotation_angle(self, sonar_data):
        if min(sonar_data) > self.sonar_threshold:
            # no obstacle, pure random
            angle_range = [0, 2 * constants.pi]

        else:
            # exists obstacle, turn back
            angle_range = [0.4 * constants.pi, 1.6 * constants.pi]
            # use left sonars to
            # if sonar_data[0] <= self.sonar_threshold:
            #     angle_range[0] = 0.8 * constants.pi
            # elif sonar_data[1] <= self.sonar_threshold:
            #     angle_range[0] = 0.6 * constants.pi
            #
            # if sonar_data[4] <= self.sonar_threshold:
            #     angle_range[1] = 1.2 * constants.pi
            # elif sonar_data[3] <= self.sonar_threshold:
            #     angle_range[1] = 1.4 * constants.pi

            if sonar_data[0] <= self.sonar_threshold:
                angle_range[0] = 1 * constants.pi
            elif sonar_data[1] <= self.sonar_threshold:
                angle_range[0] = 1 * constants.pi

            if sonar_data[4] <= self.sonar_threshold:
                angle_range[1] = 1 * constants.pi
            elif sonar_data[3] <= self.sonar_threshold:
                angle_range[1] = 1 * constants.pi

        random_angle = (angle_range[1] - angle_range[0]) * random.random() + angle_range[0]
        random_angle = self.angle_protection(random_angle)
        print 'move angle is: ', random_angle
        return random_angle



















