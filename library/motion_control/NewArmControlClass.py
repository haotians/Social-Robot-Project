# this class use the correct way of defining coordinate system.
# Some new method will be added.

import numpy as np
from scipy import constants
from scipy import linalg
import threading
import time
import NewRobotModel


class ArmControlClass(object):
    # This class defined several common motion for robot arm control.
    # Version 2015-11-11
    # The whole class is programmed based on the idea of offline programming. When a command come,
    # it get the current arm position, and plan trajectory just based on the initial state.
    # No additional feedback signal is used in the entire moving trajectory
    def __init__(self):
        # base xyz position. we don't use it
        self.position = np.array([0, 0, 0])
        # position of angles, only "self.make_a_move" will update this value
        self.angles = [0, constants.pi / 2, -constants.pi / 2.2, -constants.pi / 2, constants.pi / 1.03,
                       constants.pi / 2, constants.pi / 2.2, -constants.pi / 2, -constants.pi / 1.03]

        # self.angles = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        # self.angles = [0, constants.pi/4, -constants.pi/4.5, constants.pi/3.7, constants.pi/2.15,
        #                constants.pi/4, constants.pi/4.5, constants.pi/3.7, -constants.pi/2.15]

        # robot model class
        self.robot = NewRobotModel.RobotModel()
        # control cycle is 20 ms
        self.control_cycle = 0.02

        self.thread_temp = None
        self.record_flag = False  # a flag used to stop 'thread_temp'

        # for each unit, the speed is 0.114 rpm = 0.114 * 360 / 60 = 0.684 degree/s
        # if the control cycle is 20 ms, each unit is 0.0137 degree/(20 ms)
        # each unit is 0.088 degree
        self.speed_ratio = 0.114 * 2 * constants.pi / 60 * 0.02
        self.angle_ratio = 0.088 * 2 * constants.pi / 360

        # initial position
        self.initial_position = [0, constants.pi / 4, -constants.pi / 4.5, constants.pi / 6, constants.pi / 2.15,
                                 constants.pi / 4, constants.pi / 4.5, constants.pi / 6, -constants.pi / 2.15]

        # fold position and half_fold position
        self.half_fold_position = [0, constants.pi / 2, -constants.pi / 6, -constants.pi / 2, 2 * constants.pi / 3,
                                   constants.pi / 2, constants.pi / 6, -constants.pi / 2, -2 * constants.pi / 3]

        self.fold_position = [0, constants.pi / 1.95, -constants.pi / 2.15, -constants.pi / 2, constants.pi / 1.02,
                              constants.pi / 1.95, constants.pi / 2.05, -constants.pi / 2.08, -constants.pi / 1.01]

        self.music_initial = [0, constants.pi / 3.4, -constants.pi / 4.2, constants.pi / 3.7, constants.pi / 2.1,
                              constants.pi / 3.4, constants.pi / 4.2, constants.pi / 3.7, -constants.pi / 2.1]

        # current angles
        self.current_angles = None

    def cartesian_move(self, current_angle, vel_left, vel_right, step_length=0.001):
        # make cartesian move. velocity vector of angles is solved using jacobian and pseudo-inverse
        # vel_left: velocity vector of left hand
        # vel_right: velocity vector of right hand
        # since we are using offline programming, we can't refer to current sensor data

        angles_before = np.array(current_angle)
        angles_after = np.array(current_angle)

        # map workspace velocity to configuration space velocity
        vel_ang_left = self.workspace_velocity_to_configuration_velocity_left(angles_before, vel_left)
        vel_ang_right = self.workspace_velocity_to_configuration_velocity_right(angles_before, vel_right)

        # compute angle after one step length
        angles_after[1:5] = angles_before[1:5] + step_length * vel_ang_left
        angles_after[5:9] = angles_before[5:9] + step_length * vel_ang_right

        return angles_after

    def workspace_velocity_to_configuration_velocity_right(self, current_angle, vel_right):
        # this method map the velocity in workspace to configuration space
        vel_right = np.array(vel_right)
        # compute jacobian
        j_right_arm = self.robot.jacobian_right(current_angle)
        # compute pseudo-inverse
        j_right_arm_inv = linalg.pinv(j_right_arm)
        # compute angular velocity for each joint
        vel_ang_right = j_right_arm_inv.dot(vel_right)
        return vel_ang_right

    def workspace_velocity_to_configuration_velocity_left(self, current_angle, vel_left):
        # this method map the velocity in workspace to configuration space
        vel_left = np.array(vel_left)
        # compute jacobian
        j_left_arm = self.robot.jacobian_left(current_angle)
        # compute pseudo-inverse
        j_left_arm_inv = linalg.pinv(j_left_arm)
        # compute angular velocity for each joint
        vel_ang_left = j_left_arm_inv.dot(vel_left)
        return vel_ang_left

    def make_a_move(self, goal_angles, time_span=0.02, speed_limit=0.02):  # goal_angles=0,4left,4right
        command_list = list()
        # calculate the number of control cycle
        num_control_cycle = int(time_span / self.control_cycle)
        if num_control_cycle == 0:
            num_control_cycle = 1

        goal_angles = np.array(goal_angles)
        goal_angles = goal_angles.astype(float)
        # calculate the angle difference
        diff_angles = goal_angles - self.angles
        # find the maximum difference
        diff_max = np.max(np.abs(diff_angles))

        # determine the number of control cycle based on the maximum difference and time span
        # diff_max / num_control_cycle means the angle (in radius) travel per control cycle
        if diff_max / num_control_cycle >= speed_limit:
            num_control_cycle = int(diff_max / speed_limit)

        # calculate the angle and speed for one control cycle
        # todo: it's better to move the unit transform to self.radius_to_output
        temp_diff = diff_angles / num_control_cycle
        temp_speed = temp_diff / self.speed_ratio
        for j in range(9):
            if np.abs(temp_speed[j]) < 1:
                # set speed to a very small number
                temp_speed[j] = 1

        temp_current_angle = self.angles
        for i in range(num_control_cycle):
            temp_angles = (temp_current_angle + temp_diff) / self.angle_ratio
            # update angle and make a move
            temp_current_angle = temp_current_angle + temp_diff
            one_command = self.radius_to_output(temp_angles, temp_speed)
            command_list.append(one_command)
        self.angles = temp_current_angle
        return command_list

    def make_a_move_2(self, goal_angles, time_span=0.02, speed_limit=0.02):
        command_list = list()
        goal_angles = np.array(goal_angles)
        goal_angles = goal_angles.astype(float)
        # calculate average speed
        diff_angles = goal_angles - self.angles
        avg_speed = diff_angles / time_span

        # if goal_angles equal to current angle, return directly
        if np.max(np.abs(diff_angles)) == 0:
            for i in range(int(time_span / self.control_cycle)):
                one_command = self.radius_to_output_2(goal_angles, [speed_limit] * 9)
                command_list.append(one_command)
                # print one_command
            return command_list

        # calculate the speed contour
        # there is 3 stages for each move:
        # 1. acc to goal speed, reach angle_1
        # 2. move to angle_2, with constant speed
        # 3. dec to 0 speed, reach goal_angle
        max_speed = 0.114 * 2 * constants.pi / 60 * 1023
        temp_speed_ratio = max_speed / (1.5 * np.max(np.abs(avg_speed)))
        if temp_speed_ratio < 1:
            avg_speed *= temp_speed_ratio
            time_span /= temp_speed_ratio
        # we assume the goal speed is 1.5 * avg_speed
        goal_speed = 1.5 * avg_speed
        time_2 = 2 * np.max(np.abs(diff_angles)) / np.max(np.abs(goal_speed)) - time_span
        time_1 = (time_span - time_2) / 2

        angle_1 = self.angles + 0.5 * goal_speed * time_1
        angle_2 = angle_1 + time_2 * goal_speed

        # stage 1:
        num_cycle_1 = int(time_1 / self.control_cycle)
        for i in range(num_cycle_1):
            current_speed = goal_speed * (i + 1) / num_cycle_1
            current_angle = self.angles + 0.5 * current_speed * (i + 1) * self.control_cycle
            one_command = self.radius_to_output_2(current_angle, np.maximum(np.abs(current_speed), speed_limit))
            command_list.append(one_command)
        # print 'n1', num_cycle_1
        # stage 2:
        num_cycle_2 = int(time_2 / self.control_cycle)
        for i in range(num_cycle_2):
            current_speed = goal_speed
            current_angle = angle_1 + current_speed * (i + 1) * self.control_cycle
            one_command = self.radius_to_output_2(current_angle, np.maximum(np.abs(current_speed), speed_limit))
            command_list.append(one_command)
        # print 'n2', num_cycle_2
        # stage 3:
        num_cycle_3 = int(time_1 / self.control_cycle)
        for i in range(num_cycle_3):
            current_speed = goal_speed - goal_speed * (i + 1) / num_cycle_3
            current_angle = angle_2 + 0.5 * (goal_speed + current_speed) * (i + 1) * self.control_cycle
            one_command = self.radius_to_output_2(current_angle, np.maximum(np.abs(current_speed), speed_limit))
            command_list.append(one_command)
        # print 'n3', num_cycle_3
        self.angles = goal_angles
        one_command = self.radius_to_output_2(goal_angles, [0] * 9)
        command_list.append(one_command)
        return command_list

    def radius_to_output_2(self, angles, speed, flag=0):
        speed_ratio = 0.114 * 2 * constants.pi / 60
        angle_ratio = 0.088 * 2 * constants.pi / 360

        # the position range of servos is 0 - 4096, 2048 is the zero position
        # the sign is based on the mechanical mounting method.
        temp_angles = list()
        temp_angles.append(int(2048 + angles[1] / angle_ratio))
        temp_angles.append(int(2048 - angles[2] / angle_ratio))
        temp_angles.append(int(2048 + angles[3] / angle_ratio))
        temp_angles.append(int(2048 - angles[4] / angle_ratio))

        temp_angles.append(int(2048 - angles[5] / angle_ratio))
        temp_angles.append(int(2048 + angles[6] / angle_ratio))
        temp_angles.append(int(2048 - angles[7] / angle_ratio))
        temp_angles.append(int(2048 - angles[8] / angle_ratio))

        temp_speed = []
        for i in range(8):
            temp_speed.append(max(int(np.abs(speed[i + 1] / speed_ratio)), 5))

        # generate the proper form for transmit
        temp_output = [flag]
        for i in range(8):
            temp_output.append(temp_angles[i])
            temp_output.append(temp_speed[i])

        # print(temp_output)
        return temp_output

    def radius_to_output(self, angles, speed, flag=0):
        # the position range of servos is 0 - 4096, 2048 is the zero position
        # the sign is based on the mechanical mounting method.
        temp_angles = list()
        temp_angles.append(int(2048 + angles[1]))
        temp_angles.append(int(2048 - angles[2]))
        temp_angles.append(int(2048 + angles[3]))
        temp_angles.append(int(2048 - angles[4]))

        temp_angles.append(int(2048 - angles[5]))
        temp_angles.append(int(2048 + angles[6]))
        temp_angles.append(int(2048 - angles[7]))
        temp_angles.append(int(2048 - angles[8]))

        temp_speed = []
        for i in range(8):
            temp_speed.append(int(np.abs(speed[i + 1])))

        # generate the proper form for transmit
        temp_output = [flag]
        for i in range(8):
            temp_output.append(temp_angles[i])
            temp_output.append(temp_speed[i])

        # print(temp_output)
        return temp_output

    def output_to_radius(self, temp):
        # transform to -pi - pi. the sign is based on mechanical mounting method
        angles = [0, self.angle_ratio * (temp[1] - 2048), self.angle_ratio * (2048 - temp[3]),
                  self.angle_ratio * (temp[5] - 2048), self.angle_ratio * (2048 - temp[7]),
                  self.angle_ratio * (2048 - temp[9]), self.angle_ratio * (temp[11] - 2048),
                  self.angle_ratio * (2048 - temp[13]), self.angle_ratio * (2048 - temp[15])]
        # print angles[1:5]  #left hand
        # print angles[5:9]  #right hand
        return angles

    def set_kp_parameter(self, kp_parameter=[32, 32, 32, 32, 32, 32, 32, 32]):
        temp_para = [2]
        for i in range(8):
            temp_para.append(int(kp_parameter[i]))
            temp_para.append(int(kp_parameter[i]))
        return temp_para

    def set_ki_parameter(self, ki_parameter=[20, 20, 20, 20, 20, 20, 20, 20]):
        temp_para = [3]
        for i in range(8):
            temp_para.append(int(ki_parameter[i]))
            temp_para.append(int(ki_parameter[i]))
        return temp_para

    def set_kd_parameter(self, kd_parameter=[0, 0, 0, 0, 0, 0, 0, 0]):
        temp_para = [4]
        for i in range(8):
            temp_para.append(int(kd_parameter[i]))
            temp_para.append(int(kd_parameter[i]))
        return temp_para

    def set_pid_to_default(self):
        command_list = list()
        for i in range(30):
            kp = i + 30
            command_list.append(self.set_kp_parameter([kp] * 8))
        # for i in range(10):
        #     ki = i
        #     command_list.append(self.set_ki_parameter([ki] * 8))
        command_list.append(self.set_ki_parameter([0] * 8))
        for i in range(10):
            kd = i
            command_list.append(self.set_kd_parameter([kd] * 8))
        return command_list

    def set_pid_to_zero(self):
        self.set_kd_parameter([0, 0, 0, 0, 0, 0, 0, 0])
        self.set_ki_parameter([0, 0, 0, 0, 0, 0, 0, 0])
        self.set_kp_parameter([0, 0, 0, 0, 0, 0, 0, 0])

    def set_torque_limit(self):
        command_list = list()
        command_list.append([7] + [0] * 16)
        return command_list

    def set_no_torque(self):
        command_list = list()
        command_list.append([1] + [0] * 16)
        return command_list

    def read_reformat_file(self, path):
        # this method read and reformat as a list
        file_r = file(path, 'r')
        whole_file = file_r.readlines()
        file_data = []
        for i in range(len(whole_file)):
            data_in_str = whole_file[i].split()
            data_in_float = []
            for j in data_in_str:
                data_in_float.append(float(j))
            file_data.append(data_in_float)
        # close the file
        file_r.close()
        return file_data

    def reformat_music_data(self, data):
        new_data = list()
        for a_instant in data:
            if a_instant[1] == 0:
                temp_left = 0
            else:
                temp_left = a_instant[1] - 8

            if a_instant[2] > 0:
                temp_right = a_instant[2] + 4
            elif a_instant[2] < 0:
                temp_right = a_instant[2] + 5
            else:
                temp_right = 0

            temp = [a_instant[0], temp_left, temp_right]
            new_data.append(temp)
        return new_data

    def modify_music_file(self, left_shift, right_shift, path):
        file_data = self.read_reformat_file(path)
        file_w = file('temp_music', 'w')
        for a_data in file_data:
            temp_str = ''
            temp_str += str(a_data[0])
            temp_str += ' '
            if a_data[1] == 0:
                temp_str += str(int(a_data[1]))
            else:
                temp_str += str(int(a_data[1]) + left_shift)
            temp_str += ' '
            if a_data[2] == 0:
                temp_str += str(int(a_data[2]))
            else:
                temp_str += str(int(a_data[2]) + right_shift)
            temp_str += '\n'
            file_w.writelines(temp_str)
            file_w.flush()
        # close the file
        file_w.close()

    def build_keyboard_library(self, current_position):
        self.robot.parameters[5] = 0.500
        # this method build a simple library for play music
        keyboard_high_library = list()
        keyboard_low_library = list()

        # first, move to a proper initial position
        for j in range(25):
            current_position = self.cartesian_move(current_position, [0.0, -0.4, 0], [0.0, 0.0, 0])
            time.sleep(0.001)

        keyboard_high_library.append(list(current_position))
        for i in range(6):
            for j in range(25):
                current_position = self.cartesian_move(current_position, [0.0, -0.90, 0], [-0.1, -0.88, 0])
                time.sleep(0.001)
            keyboard_high_library.append(list(current_position))

        current_position = keyboard_high_library[0]
        for i in range(6):
            for j in range(25):
                current_position = self.cartesian_move(current_position, [0.0, 0.90, 0], [0.1, 0.92, 0])
                time.sleep(0.001)
            keyboard_high_library.insert(0, list(current_position))

        for i in keyboard_high_library:
            current_position = i
            for j in range(25):
                current_position = self.cartesian_move(current_position, [0, 0, -3.0], [0, 0, -3.0])
                time.sleep(0.001)
            keyboard_low_library.append(list(current_position))
        self.robot.parameters[5] = 0.335
        return keyboard_high_library, keyboard_low_library

    def play_music(self, path='./data/music/mother'):
        command_list = list()

        # read file and reformat as a list
        file_data = self.read_reformat_file(path)
        file_data = self.reformat_music_data(file_data)

        # define and move to initial position
        command_list += self.make_a_move_2(self.music_initial, 2)

        # scan the keyboard to get a position library with high precision
        keyboard_high_library, keyboard_low_library = self.build_keyboard_library(self.music_initial)

        # start playing
        for i in range(len(file_data)):
            if i == len(file_data) - 1:
                pass
            else:
                # each step is 0.1s
                # for left hand
                if file_data[i][1] == 0:
                    if file_data[i + 1][1] == 0:
                        try:
                            if file_data[i + 2][1] == 0:
                                target_left = self.angles
                            else:
                                # target_left = (np.array(self.angles) +
                                #                1 * np.array(keyboard_high_library[int(file_data[i+2][1])])) / 2
                                target_left = keyboard_high_library[int(file_data[i + 2][1])]
                        except IndexError:
                            target_left = self.angles
                    else:
                        target_left = keyboard_high_library[int(file_data[i + 1][1])]
                else:
                    if file_data[i - 1][1] == 0:
                        target_left = keyboard_low_library[int(file_data[i][1])]
                    elif file_data[i + 1][1] == 0:
                        target_left = keyboard_high_library[int(file_data[i][1])]
                    else:
                        target_left = self.angles
                # for right hand
                if file_data[i][2] == 0:
                    if file_data[i + 1][2] == 0:
                        try:
                            if file_data[i + 2][2] == 0:
                                target_right = self.angles
                            else:
                                # target_right = (np.array(self.angles) +
                                #                 3 * np.array(keyboard_high_library[int(file_data[i+2][2])])) / 4
                                target_right = keyboard_high_library[int(file_data[i + 2][2])]
                        except IndexError:
                            target_right = self.angles
                    else:
                        target_right = keyboard_high_library[int(file_data[i + 1][2])]
                else:
                    if file_data[i - 1][2] == 0:
                        target_right = keyboard_low_library[int(file_data[i][2])]
                    elif file_data[i + 1][2] == 0:
                        target_right = keyboard_high_library[int(file_data[i][2])]
                    else:
                        target_right = self.angles
                # target = list(target_left[0:5]) + list(target_right[5:9])
                target = list(self.music_initial[0:5]) + list(target_right[5:9])
                if i == 0:
                    command_list += self.make_a_move_2(target, 0.5)
                else:
                    command_list += self.make_a_move_2(target, 0.16, 1.6)
                    # print target
                    # command_list += self.make_a_move(target, 0.1, 0.18)

        # move to initial position
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list

    def play_music_2(self, path='./data/music/mother'):
        command_list = list()

        # read file and reformat as a list
        file_data = self.read_reformat_file(path)
        file_data = self.reformat_music_data(file_data)

        # define and move to initial position
        command_list += self.make_a_move_2(self.music_initial, 2)

        # scan the keyboard to get a position library with high precision
        keyboard_high_library, keyboard_low_library = self.build_keyboard_library(self.music_initial)

        # start playing
        for i in range(len(file_data)):
            if i == len(file_data) - 1:
                pass
            else:
                # each step is 0.1s
                # for left hand
                if file_data[i][1] == 0:
                    if file_data[i + 1][1] == 0:
                        try:
                            if file_data[i + 2][1] == 0:
                                target_left = self.angles
                            else:
                                target_left = (np.array(self.angles) +
                                               3 * np.array(keyboard_high_library[int(file_data[i + 2][1])])) / 4
                                # target_left = keyboard_high_library[int(file_data[i+2][1])]
                        except IndexError:
                            target_left = self.angles
                    else:
                        target_left = keyboard_high_library[int(file_data[i + 1][1])]
                else:
                    if file_data[i - 1][1] == 0:
                        target_left = keyboard_low_library[int(file_data[i][1])]
                    elif file_data[i + 1][1] == 0:
                        target_left = keyboard_high_library[int(file_data[i][1])]
                    else:
                        target_left = self.angles
                # for right hand
                if file_data[i][2] == 0:
                    if file_data[i + 1][2] == 0:
                        try:
                            if file_data[i + 2][2] == 0:
                                target_right = self.angles
                            else:
                                # target_right = (np.array(self.angles) +
                                #                 3 * np.array(keyboard_high_library[int(file_data[i+2][2])])) / 4
                                target_right = keyboard_high_library[int(file_data[i + 2][2])]
                        except IndexError:
                            target_right = self.angles
                    else:
                        target_right = keyboard_high_library[int(file_data[i + 1][2])]
                else:
                    if file_data[i - 1][2] == 0:
                        target_right = keyboard_low_library[int(file_data[i][2])]
                    elif file_data[i + 1][2] == 0:
                        target_right = keyboard_high_library[int(file_data[i][2])]
                    else:
                        target_right = self.angles
                target = list(target_left[0:5]) + list(target_right[5:9])
                # target = list(self.music_initial[0:5]) + list(target_right[5:9])
                # target = list(target_left[0:5]) + list(self.music_initial[5:9])
                if i == 0:
                    command_list += self.make_a_move_2(target, 0.5)
                else:
                    command_list += self.make_a_move_2(target, 0.16, 1.6)

        # move to initial position
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list

    def follow_trajectory(self, path='./data/arm_trajectory/wave'):
        if path == './data/arm_trajectory/wave' or path == './data/arm_trajectory/back_wave' \
                or path == './data/arm_trajectory/finger_point':
            move_type = 1
        else:
            move_type = 0

        command_list = list()

        # read file and reformat as a list
        file_data = self.read_reformat_file(path)

        # follow the trajectory
        initial_time = file_data[0][0] - 0.5
        for a_position in file_data:
            if a_position == []:  # in case empty lines read from outside txt file
                continue

            time_span = a_position[0] - initial_time
            initial_time = a_position[0]

            if move_type == 0:
                command_list += self.make_a_move(a_position[1:10], time_span)
            else:
                command_list += self.make_a_move_2(a_position[1:10], time_span)

        if move_type == 0:
            command_list += self.make_a_move_2(self.initial_position, 1.5)
        else:
            command_list += self.make_a_move_2(self.initial_position, 0.5)

        return command_list

    def stop_arm_move(self):
        self.make_a_move(self.angles, 0.02)

    def go_to_a_point(self, target):
        trajectory = list()
        goal_angle = self.robot.random_sample_ik(target, self.angles)
        if goal_angle is not None:
            trajectory += self.make_a_move(goal_angle, 1)
            trajectory += self.make_a_move(goal_angle, 2)
            trajectory += self.make_a_move(self.initial_position, 2)
        else:
            trajectory = self.make_a_move(self.angles, 0.5)
        return trajectory

    def point_a_point(self, target):
        goal_angle = self.robot.random_sample_point_direction(target, self.angles)
        if goal_angle is not None:
            trajectory = self.make_a_move(goal_angle, 1.5)
        else:
            trajectory = self.make_a_move(self.angles, 0.5)
        return trajectory

    def record_data(self):
        # this function keep
        file_w = file('./data/arm_trajectory/a_word', 'w')
        while self.record_flag:
            # this loop keeps running until 'record_flag' is set to be False
            temp_time = time.time()
            temp_angle = [temp_time] + self.current_angles
            # transform to proper form for txt
            temp_str = ''
            for i in temp_angle:
                temp_str += str(i)
                temp_str += ' '
            temp_str += '\n'
            file_w.writelines(temp_str)
            file_w.flush()
            # the sampling rate is about 0.15s
            time.sleep(0.02)
        # close the file
        file_w.close()

    def begin_record_pose(self):
        command_list = list()
        # start thread
        command_list.append(self.radius_to_output(self.angles, [0, 0, 0, 0, 0, 0, 0, 0, 0], 1))
        self.thread_temp = threading.Thread(target=self.record_data, name='thread_temp')  # open a thread to record data
        self.thread_temp.daemon = True
        self.record_flag = True
        self.thread_temp.start()
        return command_list

    def stop_record_pose(self):
        command_list = list()
        # start thread
        self.record_flag = False
        time.sleep(0.1)
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list


    ############################################################
    def define_quadrant_left(self, point0, point1):
        if (1.39 < point0 <= 1.74) and (-1.4 <= point1 <= 0.8):  # fold region
            return 0
        elif (-1.57 <= point0 <= 0.005) and (-1.30 <= point1 <= 0.005):
            return 1
        elif (-0.005 < point0 <= 1.57) and (-0.785 <= point1 < 0.005):
            return 2
        else:
            return 5


    def define_quadrant_right(self, point0, point1):
        if (1.39 < point0 <= 1.74) and (-0.8 <= point1 <= 1.4):  # fold region
            return 0
        elif (-1.57 <= point0 <= 0.005) and (-0.005 <= point1 < 1.30):
            return 1
        elif (-0.005 < point0 <= 1.39) and (-0.005 < point1 <= 0.785):
            return 2
        else:
            return 5


    def which_quadrant(self, goal, current):    #[0, 4left, 4right]
        p_list = [goal, current]  # [[0, 4left, 4right], [0, 4left, 4right]]
        q_list = list()

        for i in range(2):
            point = p_list[i]  # [0, 4left, 4right]
            if i == 0:    # goal
                goal_quad_l = self.define_quadrant_left(point[1], point[2])
                goal_quad_r = self.define_quadrant_right(point[5], point[6])
                q_list.append(goal_quad_l)
                q_list.append(goal_quad_r)
            elif i == 1:    # current
                current_quad_l = self.define_quadrant_left(point[1], point[2])
                current_quad_r = self.define_quadrant_right(point[5], point[6])
                q_list.append(current_quad_l)
                q_list.append(current_quad_r)

        return [q_list[0], q_list[1]], [q_list[2], q_list[3]]


    def make_a_move_quadrant(self, goal_position, goal_quad, current_position, current_quad, time_span):
        # goal_quad = [1, 2]
        # goal_position = [0, 4left, 4right]

        # g = [0, 0.785,-0.698,0.523,1.461, 0.785,0.698,0.523,-1.461]
        # c = [0, 0,0,0,0, 0,0,0,0]
        init_position = [0, 0.785, -0.698, 0.523, 1.461, 0.785, 0.698, 0.523, -1.461]
        fully_fold = [0, 1.57, -1.4, -1.57, 2.9, 1.57, 1.4, -1.57, -2.9]

        left_list = list()
        right_list = list()
        goal_list = list()
        command_list = list()

        for i in range(2):
            # in the same quadrant
            if goal_quad[i] == current_quad[i]:
                if i == 0:  #left
                    left_list.append(goal_position[1:5])
                    left_list.append(goal_position[1:5])
                elif i == 1:    #right
                    right_list.append(goal_position[5:9])
                    right_list.append(goal_position[5:9])

            # not in the same quadrant
            # quadrant 1 <-> quadrant 2
            elif (goal_quad[i] == 1 and current_quad[i] == 2) or (goal_quad[i] == 2 and current_quad[i] == 1):
                if i == 0:
                    left_list.append(init_position[1:5])
                    left_list.append(goal_position[1:5])
                elif i == 1:
                    right_list.append(init_position[5:9])
                    right_list.append(goal_position[5:9])

            # one in quadrant 0
            elif goal_quad[i] == 0 or current_quad[i] == 0:
                if i == 0:
                    left_list.append(fully_fold[1:5])
                    left_list.append(goal_position[1:5])
                elif i == 1:
                    right_list.append(fully_fold[5:9])
                    right_list.append(goal_position[5:9])

            else:
                # back to fully_fold position
                if i == 0:
                    left_list.append(fully_fold[1:5])
                    left_list.append(goal_position[1:5])
                elif i == 1:
                    right_list.append(fully_fold[5:9])
                    right_list.append(goal_position[5:9])

        for i in range(2):
            tmp = left_list[i]
            tmp.extend(right_list[i])
            tmp.insert(0, 0)
            goal_list.append(tmp)
            command_list += self.make_a_move(goal_list[i], time_span)

        print "goal_list: "
        print goal_list

        return command_list


    def transition(self, current_position, path='./data/test/move'):
        print "transition()..."
        file_data = self.read_reformat_file(path)   #[time, 0, 4left, 4right]

        # 1. get goal position
        goal_position = file_data[0]    #[time, 0, 4left, 4right]
        initial_time = goal_position[0] - 0.5
        time_span = goal_position[0] - initial_time
        goal_position = goal_position[1:10]     #[0, 4left, 4right]
        print "goal_position: ", goal_position
        print "current_position: ", current_position

        # 3. define quadrant of different positions
        goal_quad, current_quad = self.which_quadrant(goal_position, current_position)
        print "goal_quad, current_quad: ", goal_quad, current_quad

        # 4. make a move base on the quadrant
        command_list = self.make_a_move_quadrant(goal_position, goal_quad, current_position, current_quad, time_span=3)

        return command_list
    ############################################################


    def create_control_data(self, data):
        if self.current_angles is not None:
            self.angles = self.current_angles

        trajectory = None
        if data[0] == 1:
            # update current angle
            # self.angles = self.current_angles
            trajectory = self.make_a_move(self.initial_position, 2)
        elif data[0] == 2:
            # follow trajectory
            if data[1] == 0:
                trajectory = self.follow_trajectory()
            else:
                trajectory = self.follow_trajectory(data[1])
        elif data[0] == 3:
            # begin record a move
            trajectory = self.begin_record_pose()
        elif data[0] == 4:
            # stop record a move
            trajectory = self.stop_record_pose()
        elif data[0] == 5:
            # play two hand music
            if data[1] == 0:
                trajectory = self.play_music_2()
            else:
                trajectory = self.play_music_2(data[1])
        elif data[0] == 6:
            # move to certain angles
            trajectory = self.make_a_move_2(data[1:10], 4)
        elif data[0] == 7:
            # set pid to initial
            trajectory = self.set_pid_to_default()
        elif data[0] == 10:
            # just do nothing
            trajectory = self.make_a_move(self.angles, 0.2)
        elif data[0] == 11:
            # trajectory = self.make_a_move(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), 2)
            # return to close position
            trajectory = self.make_a_move_2(self.half_fold_position, 2)
            trajectory += self.make_a_move_2(self.fold_position, 2)
        elif data[0] == 12:
            # trajectory = self.make_a_move(np.array([0, 0, 0, 0, 0, 0, 0, 0, 0]), 2)
            trajectory = self.make_a_move_2(self.half_fold_position, 2)
            trajectory += self.make_a_move_2(self.initial_position, 2)
        elif data[0] == 13:
            trajectory = self.make_a_move_2(self.half_fold_position, 2)
        elif data[0] == 14:
            trajectory = self.make_a_move_2(self.initial_position, 2)
        elif data[0] == 15:
            trajectory = self.make_a_move_2(self.fold_position, 2)
        elif data[0] == 16:
            trajectory = self.go_to_a_point(data[1:4])
        elif data[0] == 17:
            trajectory = self.point_a_point(data[1:4])
        elif data[0] == 18:
            trajectory = self.make_a_move_2(self.music_initial, 2)
        elif data[0] == 19:
            trajectory = self.set_torque_limit()
        elif data[0] == 20:
            trajectory = self.set_no_torque()


        elif data[0] == 29:
            trajectory = self.transition(self.angles)

        return trajectory


if __name__ == '__main__':
    arm = ArmControlClass()
    # arm.modify_music_file(-7, 0, 'farewell')
