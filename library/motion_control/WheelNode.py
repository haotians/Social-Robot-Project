# this class is used to listen and record
import time
import numpy as np

import components.Components
import WheelControlClass
from scipy import constants
import math


class WheelNode(components.Components.Node):

    def __init__(self, master_object):
        components.Components.Node.__init__(self, master_object)
        self.name = 'wheel_control'
        self.wheel_object = WheelControlClass.WheelControlClass()
        self.current_position = [0, 0, 0]
        self.current_position_time = 0
        self.goal_position = None
        self.position_move_stage = 0

        self.timer_counter = 0
        self.sleep_time = 0.02

        self.watch_dog_time = 10

    def _node_run(self):

        print 'wheel sys started'
        time.sleep(1)

        last_command_time = 0

        while self.thread_active:

            # Part 1: read all message:
            messages = self.get_messages_from_all_topics()

            # Part 2: use these messages to generate commands for each topic

            # Part 2.1: preprocess data, get command for wheel
            current_time = time.time()
            wheel_command = None
            for i in range(len(messages)):
                if messages[i] is not None:
                    # print(messages[i])
                    msg_time, msg_type, data, source = self.message_object.message_dewarp(messages[i])
                    if msg_type == 32:
                        wheel_command = data[0:4]
                        print 'wheel_command:', wheel_command
                        # print 'wheel_node_current', self.current_position
                    if msg_type == 71:
                        self.current_position = data
                        self.current_position_time = msg_time

            # Part 2.2 generate commands
            # data[0] == 0 : UI control
            # data[0] == 1 : straight locomotion
            # data[0] == 2 : circle locomotion
            # data[0] == 3 : move to certain position (x,y,theta)
            #   for case 3: stage 1: rotation, stage 2: straight move, stage 3: rotation, stage 0: finish/ no command

            raw_command = None
            if wheel_command is not None:
                raw_command = self.create_control_data(wheel_command)
                last_command_time = time.time()

            # check whether in the mode of 3 (move to certain position)
            if self.position_move_stage is not 0:
                # this timer counter is used for generating delay between different move stage
                if self.timer_counter > 0:
                    # wait some time
                    self.timer_counter -= 1
                else:
                    self.timer_counter = 0
                    # print(self.current_position)
                    raw_command = self.simple_planning_for_locomotion(self.goal_position, self.current_position)
                    current_time = time.time()
                    # a simple protection for unable reach target
                    if current_time - last_command_time >= self.watch_dog_time:
                        self.position_move_stage = 0
                        print 'unable to move to target position'

            # Part 3: output commands
            commands = []
            if raw_command is not None:
                commands.append(self.message_object.message_warp("wheel_to_serial", raw_command))
                # print 'wheel_output:', commands
            commands.append(self.message_object.message_warp('wheel_move_stage', self.position_move_stage))
            self.output_all_messages(commands)

            # Part 4: report to master
            self.output_status_to_master(False)
            time.sleep(self.sleep_time)

    def create_control_data(self, data):
        trajectory = None
        self.position_move_stage = 0
        self.timer_counter = 0
        if data[0] == 0:  # UI control
            trajectory = [self.wheel_object.ui_to_wheel(data[1], data[2])]
        elif data[0] == 1:  # straight locomotion
            trajectory = [self.wheel_object.straight(data[1], data[2])]
        elif data[0] == 2:  # circular locomotion
            trajectory = [self.wheel_object.circle(data[1], data[2], data[3])]
        elif data[0] == 3:  # move to a given position
            self.position_move_stage = 1.0
            data[3] = self.angle_protection(data[3])
            self.goal_position = [data[1], data[2], data[3]]

        return trajectory

    def simple_planning_for_locomotion(self, goal_position, current_position):
        # this method aims to plan a robot move from one position to another position
        # the whole move have three stage: 1 rotate, 2 straight move, 3 rotate
        trajectory = None
        if self.position_move_stage == 1.0:
            if abs(goal_position[0] - current_position[0]) + abs(goal_position[1] - current_position[1]) <= 0.1:
                # if current position and goal position are close enough, directly go to stage 3
                self.position_move_stage = 3.0
            else:
                # first, calculate the target angle and rotate
                goal_angle = np.arctan2(goal_position[1] - current_position[1], goal_position[0] - current_position[0])
                trajectory = self.rotate_to_goal_angle(goal_angle, current_position[2])
                self.position_move_stage = 1.1

        elif self.position_move_stage == 1.1:
            # wait until the robot have rotated to desired angle
            goal_angle = np.arctan2(goal_position[1] - current_position[1], goal_position[0] - current_position[0])
            if abs(goal_angle - current_position[2]) <= 0.1 or \
               abs(goal_angle - current_position[2] + 2 * constants.pi) <= 0.1 or \
               abs(goal_angle - current_position[2] - 2 * constants.pi) <= 0.1:
                self.position_move_stage = 2.0
                self.timer_counter = int(0.5 / self.sleep_time)

        elif self.position_move_stage == 2.0:
            # straight move
            trajectory = self.straight_move_to_a_point(goal_position, current_position)
            self.position_move_stage = 2.1
            # print('goal_position_2')
            # print(goal_position)
            # print('current_position_2')
            # print(current_position)

        elif self.position_move_stage == 2.1:
            # wait until the robot have moved to desired position
            # todo: this stage may have some problems, since the minimum difference may greater than 0.1
            if abs(goal_position[0] - current_position[0]) + abs(goal_position[1] - current_position[1]) <= 0.2:
                self.position_move_stage = 3.0
                self.timer_counter = int(1.0 / self.sleep_time)

        elif self.position_move_stage == 3.0:
            # rotate to desire angle
            trajectory = self.rotate_to_goal_angle(goal_position[2], current_position[2])
            self.position_move_stage = 3.1
            # print('goal_position_3')
            # print(goal_position)
            # print('current_position_3')
            # print(current_position)

        elif self.position_move_stage == 3.1:
            # wait until the robot have rotated to desired position
            if abs(goal_position[2] - current_position[2]) <= 0.02 or \
               abs(goal_position[2] - current_position[2] + 2 * constants.pi) <= 0.02 or \
               abs(goal_position[2] - current_position[2] - 2 * constants.pi) <= 0.02:
                self.position_move_stage = 0
        return trajectory

    def straight_move_to_a_point(self, goal_position, current_position, speed=0.1):
        # a simple method to calculate the distance need to move
        trajectory = list()
        distance = np.sqrt((goal_position[0] - current_position[0]) ** 2 +
                           (goal_position[1] - current_position[1]) ** 2)
        trajectory.append(self.wheel_object.straight(distance, speed))
        return trajectory

    def rotate_to_goal_angle(self, goal_angle, current_angle, speed=0.1):
        # a simple method to rotate a certain angle
        trajectory = list()
        delta_angle = goal_angle - current_angle
        delta_angle = self.angle_protection(delta_angle)
        trajectory.append(self.wheel_object.circle(delta_angle, 0, speed))
        return trajectory

    def angle_protection(self, angle):
        # a simple angle protection, make sure angle is between -pi ~ pi
        while angle > constants.pi:
            angle -= 2 * constants.pi
        while angle <= -constants.pi:
            angle += 2 * constants.pi
        return angle

