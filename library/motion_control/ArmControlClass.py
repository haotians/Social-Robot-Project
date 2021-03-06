__author__ = 'root'

import numpy as np
from scipy import constants
from scipy import linalg
import threading
import time

import RobotModel


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

        self.angles = [0, -constants.pi/2, -constants.pi/2.2, constants.pi/2, constants.pi/1.03, 0,
                       -constants.pi/2, constants.pi/2.2, constants.pi/2, -constants.pi/1.03, 0]

        self.angles = [0, 0,0,0,0, 0, 0,0,0,0, 0]

        # self.angles = [0, -constants.pi/4, -constants.pi/4.5, -constants.pi/3.7, constants.pi/2.15, 0,
        #                -constants.pi/4, constants.pi/4.5, -constants.pi/3.7, -constants.pi/2.15, 0]

        self.index = [1, 2, 3, 4, 6, 7, 8, 9]
        # the geometry parameter of the robot. They are: heights of shoulder, width of shoulder,
        # length of shoulder joint1, length of shoulder joint2, length of upper arm, length of lower arm.
        self.model_parameter = np.array([0.2, 0.49, 0.058, 0.05, 0.20, 0.33])
        # self.model_parameter = np.array([0.2, 0.49, 0.06, 0.05, 0.20, 0.695])
        # self.model_parameter = np.array([0.2, 0.49, 0.06, 0.05, 0.175, 0.725])
        # robot model class
        self.robot = RobotModel.RobotModel()
        # control cycle is 20 ms
        self.control_cycle = 20

        self.thread_temp = None
        self.record_flag = False  # a flag used to stop 'thread_temp'
        self.path = 'temp_data'  # just for transmit the path between different threads

        # for each unit, the speed is 0.114 rpm = 0.114 * 360 / 60 = 0.684 degree/s
        # if the control cycle is 20 ms, each unit is 0.0137 degree/(20 ms)
        # each unit is 0.088 degree
        self.speed_ratio = 0.114 * 2 * constants.pi / 60 * 0.02
        self.angle_ratio = 0.088 * 2 * constants.pi / 360

        # initial position
        self.initial_position = [0, -constants.pi/4, -constants.pi/4.5, -constants.pi/3.7, constants.pi/2.15, 0,
                                 -constants.pi/4, constants.pi/4.5, -constants.pi/3.7, -constants.pi/2.15, 0]

        # fold position and half_fold position
        self.half_fold_position = [0, -constants.pi/2, -constants.pi/6, constants.pi/2,  2*constants.pi/3, 0,
                                   -constants.pi/2, constants.pi/6, constants.pi/2, -2*constants.pi/3, 0]

        self.fold_position = [0, -constants.pi/2, -constants.pi/2.2, constants.pi/2, constants.pi/1.03, 0,
                              -constants.pi/2, constants.pi/2.2, constants.pi/2, -constants.pi/1.03, 0]

        self.music_initial = [0, -constants.pi/4, -constants.pi/4.5, -constants.pi/3.7, constants.pi/2.15, 0,
                              -constants.pi/4, constants.pi/4.5, -constants.pi/3.7, -constants.pi/2.15, 0]

        # current angles
        self.current_angles = list()

    def update_current_angles(self, data):
        self.current_angles = self.get_arm_position(data)

    def jacobian_left(self, angles):
        # calculate left hand jacobian.
        # it is generated by matlab symbolic toolbox. don't try to read this method...
        angle1 = angles[0]
        angle2 = angles[1]
        angle3 = angles[2]
        angle4 = angles[3]
        angle5 = angles[4]

        shoulder_x = self.model_parameter[0]
        shoulder_y = self.model_parameter[1]
        shoulder1 = self.model_parameter[2]
        shoulder2 = self.model_parameter[3]
        upper_arm = self.model_parameter[4]
        lower_arm = self.model_parameter[5]

        t2 = np.sin(angle1)
        t3 = np.sin(angle3)
        t4 = np.cos(angle1)
        t5 = np.cos(angle2)
        t6 = np.cos(angle3)
        t7 = t2*t6
        t8 = t3*t4*t5
        t9 = t7+t8
        t10 = np.sin(angle2)
        t11 = np.cos(angle4)
        t12 = np.sin(angle5)
        t13 = np.cos(angle5)
        t14 = np.sin(angle4)
        t15 = t3*t4
        t16 = t2*t5*t6
        t17 = t15+t16
        t18 = t4*t6
        t20 = t2*t3*t5
        t19 = t18-t20
        t21 = t14*t17
        t22 = t2*t10*t11
        t23 = t21+t22
        t24 = shoulder2*t3*t10
        t25 = t3*t10*upper_arm
        t26 = lower_arm*t3*t10*t13
        t27 = lower_arm*t6*t10*t12*t14
        t28 = t24+t25+t26+t27-lower_arm*t5*t11*t12
        t29 = t2*t3
        t31 = t4*t5*t6
        t30 = t29-t31
        t32 = t14*t30
        t33 = t32-t4*t10*t11
        j_left = np.array([1.0, 0.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.0, 0.0, 1.0,
                           shoulder1*t2+shoulder2*t9+shoulder_x*t2+t9*upper_arm+lower_arm*(t9*t13-t12*t33), -shoulder1*t4-shoulder2*t19-shoulder_x*t4-t19*upper_arm-lower_arm*(t13*t19-t12*t23), 0.0,
                           -t2*t28, t4*t28, -lower_arm*(t12*(t10*t11+t5*t6*t14)+t3*t5*t13)-shoulder2*t3*t5-t3*t5*upper_arm,
                           lower_arm*(t13*t17+t12*t14*t19)+shoulder2*t17+t17*upper_arm, lower_arm*(t13*t30+t9*t12*t14)+shoulder2*t30+t30*upper_arm, -t10*(shoulder2*t6+t6*upper_arm+lower_arm*t6*t13-lower_arm*t3*t12*t14),
                           lower_arm*t12*(t11*t17-t2*t10*t14), lower_arm*t12*(t11*t30+t4*t10*t14), -lower_arm*t12*(t5*t14+t6*t10*t11),
                           lower_arm*(t12*t19+t13*t23), lower_arm*(t9*t12+t13*t33), lower_arm*(t13*(t5*t11-t6*t10*t14)+t3*t10*t12),
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0])
        j_left = j_left.reshape(12, 3)
        j_left = j_left.T
        j_left_arm = j_left[:, 4:8]
        return j_left_arm

    def jacobian_right(self, angles):
        # calculate right hand jacobian.
        # it is generated by matlab symbolic toolbox. don't try to read this method...
        angle1 = angles[0]
        angle7 = angles[6]
        angle8 = angles[7]
        angle9 = angles[8]
        angle10 = angles[9]

        shoulder_x = self.model_parameter[0]
        shoulder_y = self.model_parameter[1]
        shoulder1 = self.model_parameter[2]
        shoulder2 = self.model_parameter[3]
        upper_arm = self.model_parameter[4]
        lower_arm = self.model_parameter[5]

        t2 = np.sin(angle1)
        t3 = np.sin(angle8)
        t4 = np.cos(angle1)
        t5 = np.cos(angle7)
        t6 = np.cos(angle8)
        t7 = t2*t6
        t8 = t3*t4*t5
        t9 = t7+t8
        t10 = np.sin(angle7)
        t11 = np.cos(angle9)
        t12 = np.sin(angle10)
        t13 = np.cos(angle10)
        t14 = np.sin(angle9)
        t15 = t3*t4
        t16 = t2*t5*t6
        t17 = t15+t16
        t18 = t4*t6
        t20 = t2*t3*t5
        t19 = t18-t20
        t21 = t14*t17
        t22 = t2*t10*t11
        t23 = t21+t22
        t24 = shoulder2*t3*t10
        t25 = t3*t10*upper_arm
        t26 = lower_arm*t3*t10*t13
        t27 = lower_arm*t6*t10*t12*t14
        t28 = t24+t25+t26+t27-lower_arm*t5*t11*t12
        t29 = t2*t3
        t31 = t4*t5*t6
        t30 = t29-t31
        t32 = t14*t30
        t33 = t32-t4*t10*t11
        j_right = np.array([1.0, 0.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 0.0, 1.0,
                            -shoulder1*t2-shoulder2*t9-shoulder_x*t2-t9*upper_arm-lower_arm*(t9*t13-t12*t33), shoulder1*t4+shoulder2*t19+shoulder_x*t4+t19*upper_arm+lower_arm*(t13*t19-t12*t23), 0.0,
                            0.0, 0.0, 0.0,
                            0.0, 0.0, 0.0,
                            0.0, 0.0, 0.0,
                            0.0, 0.0, 0.0,
                            t2*t28, -t4*t28, lower_arm*(t12*(t10*t11+t5*t6*t14)+t3*t5*t13)+shoulder2*t3*t5+t3*t5*upper_arm,
                            -lower_arm*(t13*t17+t12*t14*t19)-shoulder2*t17-t17*upper_arm, -lower_arm*(t13*t30+t9*t12*t14)-shoulder2*t30-t30*upper_arm, t10*(shoulder2*t6+t6*upper_arm+lower_arm*t6*t13-lower_arm*t3*t12*t14),
                            -lower_arm*t12*(t11*t17-t2*t10*t14), -lower_arm*t12*(t11*t30+t4*t10*t14), lower_arm*t12*(t5*t14+t6*t10*t11),
                            -lower_arm*(t12*t19+t13*t23), -lower_arm*(t9*t12+t13*t33), -lower_arm*(t13*(t5*t11-t6*t10*t14)+t3*t10*t12)])

        j_right = j_right.reshape(12, 3)
        j_right = j_right.T
        j_right_arm = j_right[:, 8:12]
        return j_right_arm

    def cartesian_move(self, vel_left, vel_right, step_length=0.001):
        # make cartesian move. velocity vector of angles is solved using jacobian and pseudo-inverse
        # vel_left: velocity vector of left hand
        # vel_right: velocity vector of right hand
        # since we are using offline programming, we can't refer to current sensor data

        angles_before = np.array(self.angles)
        angles_after = np.array(self.angles)

        # compute current hand position
        self.robot.set_angles(angles_before)
        self.robot.forward_kinematics()
        hand_l_before = self.robot.links[5].position
        hand_r_before = self.robot.links[10].position

        # map workspace velocity to configuration space velocity
        vel_ang_left = self.workspace_to_configuration_velocity_left(self.angles, vel_left)
        vel_ang_right = self.workspace_to_configuration_velocity_right(self.angles, vel_right)

        # compute angle after one step length
        angles_after[1:5] = angles_before[1:5] + step_length * vel_ang_left
        angles_after[6:10] = angles_before[6:10] + step_length * vel_ang_right

        # compute hand position after move
        self.robot.set_angles(angles_after)
        self.robot.forward_kinematics()
        hand_l_after = self.robot.links[5].position
        hand_r_after = self.robot.links[10].position

        # compute the difference between forward kinematics and cartesian move
        diff_position_l = (hand_l_after - hand_l_before) / step_length
        diff_position_r = (hand_r_after - hand_r_before) / step_length
        cost_value = (diff_position_l - vel_left).dot(diff_position_l - vel_left)
        cost_value = cost_value + (diff_position_r - vel_right).dot(diff_position_r - vel_right)

        # and we also do not want the angles changes suddenly. So add another term to cost_value
        cost_value = cost_value + (angles_after - angles_before).dot(angles_after - angles_before)

        # avoid exceed limits
        if np.max(np.abs(angles_after)) <= constants.pi / 1.5 and cost_value < 0.05:
            # move to new angles
            self.make_a_move(angles_after)
            # print(angles_after)

    def cartesian_move_without_move(self, current_angle, vel_left, vel_right, step_length=0.001):
        # make cartesian move. velocity vector of angles is solved using jacobian and pseudo-inverse
        # vel_left: velocity vector of left hand
        # vel_right: velocity vector of right hand
        # since we are using offline programming, we can't refer to current sensor data

        angles_before = np.array(current_angle)
        angles_after = np.array(current_angle)

        # map workspace velocity to configuration space velocity
        vel_ang_left = self.workspace_to_configuration_velocity_left(angles_before, vel_left)
        vel_ang_right = self.workspace_to_configuration_velocity_right(angles_before, vel_right)

        # compute angle after one step length
        angles_after[1:5] = angles_before[1:5] + step_length * vel_ang_left
        angles_after[6:10] = angles_before[6:10] + step_length * vel_ang_right

        # compute current hand position
        self.robot.set_angles(angles_before)
        self.robot.forward_kinematics()
        hand_l_before = self.robot.links[5].position
        hand_r_before = self.robot.links[10].position

        # compute hand position after move
        self.robot.set_angles(angles_after)
        self.robot.forward_kinematics()
        hand_l_after = self.robot.links[5].position
        hand_r_after = self.robot.links[10].position

        # compute the difference between forward kinematics and cartesian move
        diff_position_l = (hand_l_after - hand_l_before) / step_length
        diff_position_r = (hand_r_after - hand_r_before) / step_length
        cost_value = (diff_position_l - vel_left).dot(diff_position_l - vel_left)
        cost_value = cost_value + (diff_position_r - vel_right).dot(diff_position_r - vel_right)

        # and we also do not want the angles changes suddenly. So add another term to cost_value
        cost_value = cost_value + (angles_after - angles_before).dot(angles_after - angles_before)
        # avoid exceed limits
        if np.max(np.abs(angles_after)) <= constants.pi / 1.5 and cost_value < 0.05:
            # move to new angles
            output_angle = angles_after
        else:
            output_angle = angles_before

        return output_angle

    def workspace_to_configuration_velocity_right(self, current_angle, vel_right):
        # this method map the velocity in workspace to configuration space
        vel_right = np.array(vel_right)
        # compute jacobian
        j_right_arm = self.jacobian_right(current_angle)
        # compute pseudo-inverse
        j_right_arm_inv = linalg.pinv(j_right_arm)
        # compute angular velocity for each joint
        vel_ang_right = j_right_arm_inv.dot(vel_right)
        return vel_ang_right

    def workspace_to_configuration_velocity_left(self, current_angle, vel_left):
        # this method map the velocity in workspace to configuration space
        vel_left = np.array(vel_left)
        # compute jacobian
        j_left_arm = self.jacobian_left(current_angle)
        # compute pseudo-inverse
        j_left_arm_inv = linalg.pinv(j_left_arm)
        # compute angular velocity for each joint
        vel_ang_left = j_left_arm_inv.dot(vel_left)
        return vel_ang_left

    def make_a_move(self, goal_angles, time_span=0.02, speed_limit=0.02):
        command_list = list()
        # calculate the number of control cycle
        num_control_cycle = int(time_span * 1000 / self.control_cycle)

        goal_angles = np.array(goal_angles)
        # calculate the angle difference
        diff_angles = goal_angles - self.angles
        # find the maximum difference
        diff_max = np.max(np.abs(diff_angles))

        # determine the number of control cycle based on the maximum difference and time span
        # diff_max / num_control_cycle means the angle (in radius) travel per control cycle
        if diff_max / num_control_cycle >= speed_limit:
            num_control_cycle = int(diff_max / speed_limit)

        temp_current_angle = self.angles
        for i in range(num_control_cycle):
            # calculate the angle and speed for one control cycle
            temp_diff = diff_angles / num_control_cycle
            temp_speed = temp_diff / self.speed_ratio
            for j in range(11):
                if np.abs(temp_speed[j]) < 1:
                    # set speed to a very small number
                    temp_speed[j] = 1
            temp_angles = (temp_current_angle + temp_diff) / self.angle_ratio
            # update angle and make a move
            temp_current_angle = temp_current_angle + temp_diff
            one_command = self.transmit_data(temp_angles, temp_speed)
            command_list.append(one_command)
        self.angles = temp_current_angle
        return command_list

    def transmit_data(self, angles, speed, flag=0):
        # the position range of servos is 0 - 4096, 2048 is the zero position
        # the sign is based on the mechanical mounting method.
        temp_angles = list()
        temp_angles.append(int(2048 - angles[1]))
        temp_angles.append(int(2048 - angles[2]))
        temp_angles.append(int(2048 - angles[3]))
        temp_angles.append(int(2048 - angles[4]))

        temp_angles.append(int(2048 + angles[6]))
        temp_angles.append(int(2048 - angles[7]))
        temp_angles.append(int(2048 + angles[8]))
        temp_angles.append(int(2048 - angles[9]))

        temp_speed = []
        for i in self.index:
            temp_speed.append(int(np.abs(speed[i])))

        # generate the proper form for transmit
        temp_output = [flag]
        for i in range(8):
            temp_output.append(temp_angles[i])
            temp_output.append(temp_speed[i])

        # print(temp_output)
        return temp_output

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
        for i in range(60):
            command_list.append(self.set_kp_parameter([i, i, i, i, i, i, i, i]))
        # for i in range(21):
        #     command_list.append(self.set_ki_parameter([i, i, i, i, i, i, i, i]))
        for i in range(10):
            command_list.append(self.set_kd_parameter([i, i, i, i, i, i, i, i]))
        command_list.append(self.set_ki_parameter([0, 0, 0, 0, 0, 0, 0, 0]))
        # command_list.append(self.set_kd_parameter([0, 0, 0, 0, 0, 0, 0, 0]))
        return command_list

    def set_pid_to_zero(self):
        self.set_kd_parameter([0, 0, 0, 0, 0, 0, 0, 0])
        self.set_ki_parameter([0, 0, 0, 0, 0, 0, 0, 0])
        self.set_kp_parameter([0, 0, 0, 0, 0, 0, 0, 0])

    def follow_trajectory(self, path='temp_data'):
        command_list = list()

        file_r = file(path, 'r')
        temp_file = file_r.readlines()

        for i in range(len(temp_file)):
            temp_data = temp_file[i].split()
            temp_angle = []
            for j in temp_data:
                temp_angle.append(float(j))
            command_list += self.make_a_move(np.array(temp_angle), 0.04)
            time.sleep(0.0001)
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list

    def begin_record_pose(self, path='temp_data'):
        command_list = list()
        # start thread
        command_list.append(self.transmit_data(self.angles, [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], 1))
        self.thread_temp = threading.Thread(target=self.record_data, name='thread_temp')  # open a thread to record data
        self.thread_temp.daemon = True
        self.record_flag = True
        self.path = path
        self.thread_temp.start()
        return command_list

    def stop_record_pose(self):
        command_list = list()
        # start thread
        self.record_flag = False
        time.sleep(0.1)
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list

    def begin_pure_record(self, path='temp_data'):
        # start thread
        self.thread_temp = threading.Thread(target=self.record_data, name='thread_temp')  # open a thread to record data
        self.thread_temp.daemon = True
        self.record_flag = True
        self.path = path
        self.thread_temp.start()

    def stop_pure_record(self):
        # stop thread
        self.record_flag = False

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
        return file_data

    def reformat_music_data(self, data):
        new_data = list()
        for a_instant in data:
            if a_instant[1] == 0:
                temp_left = 0
            else:
                temp_left = a_instant[1] - 4

            if a_instant[2] > 0:
                temp_right = a_instant[2] + 4
            elif a_instant[2] < 0:
                temp_right = a_instant[2] + 5
            else:
                temp_right = 0

            temp = [a_instant[0], temp_left, temp_right]
            new_data.append(temp)
        return new_data

    def build_keyboard_library(self, current_position):
        # this method build a simple library for play music
        keyboard_high_library = list()
        keyboard_low_library = list()

        # first, move to a proper initial position
        for j in range(25):
            current_position = self.cartesian_move_without_move(current_position, [0.0, -0.2, -0.5], [0.0, -0.1, 0.5])
            time.sleep(0.001)

        keyboard_high_library.append(list(current_position))
        for i in range(9):
            for j in range(25):
                current_position = self.cartesian_move_without_move(current_position, [0.90, 0.05, 0], [0.84, 0, 0])
                time.sleep(0.001)
            keyboard_high_library.append(list(current_position))

        current_position = keyboard_high_library[0]
        for i in range(6):
            for j in range(25):
                current_position = self.cartesian_move_without_move(current_position, [-0.91, 0, 0], [-0.91, 0.1, 0])
                time.sleep(0.001)
            keyboard_high_library.insert(0, list(current_position))

        for i in keyboard_high_library:
            current_position = i
            for j in range(25):
                current_position = self.cartesian_move_without_move(current_position, [0, 0, -4.5], [0, 0, -5.9])
                time.sleep(0.001)
            keyboard_low_library.append(list(current_position))
        return keyboard_high_library, keyboard_low_library

    def build_keyboard_library_2(self, current_position):
        # this method build a simple library for play music
        keyboard_high_library = list()
        keyboard_low_library = list()

        # first, move to a proper initial position
        for j in range(25):
            current_position = self.cartesian_move_without_move(current_position, [0, 0, 0.3], [1.35, 0, -0.65])
            time.sleep(0.001)

        keyboard_high_library.append(list(current_position))
        for i in range(20):
            for j in range(25):
                current_position = self.cartesian_move_without_move(current_position, [0.94, 0, 0], [0.98, 0, 0])
                time.sleep(0.001)
            keyboard_high_library.append(list(current_position))
            print(current_position)

        for i in keyboard_high_library:
            current_position = i
            for j in range(25):
                current_position = self.cartesian_move_without_move(current_position, [0, 0, -2.3], [0, 0, -2.3])
                time.sleep(0.001)
            keyboard_low_library.append(list(current_position))
        return keyboard_high_library, keyboard_low_library

    def play_two_hand_music(self, path='./data/music_2'):
        command_list = list()

        # read file and reformat as a list
        file_data = self.read_reformat_file(path)

        # define and move to initial position
        initial_position = [0, -constants.pi/2.8, -constants.pi/2, - 0 * constants.pi/3, constants.pi/3, 0,
                            -constants.pi/2.8, constants.pi/2, - 0 * constants.pi/3, -constants.pi/3, 0]
        command_list += self.make_a_move(self.initial_position, 2)
        command_list += self.make_a_move(initial_position, 2)

        # scan the keyboard to get a position library with high precision
        keyboard_high_library, keyboard_low_library = self.build_keyboard_library(initial_position)

        # start playing
        for i in range(len(file_data)):
            if i == len(file_data) - 1:
                pass
            else:
                # for the first half cycle, 0.1s
                # for left hand
                if file_data[i][1] == 0:
                    if file_data[i+1][1] == 0:
                        target_left = self.angles
                    else:
                        target_left = keyboard_high_library[int(file_data[i+1][1] - 1)]
                else:
                    if file_data[i-1][1] == 0:
                        target_left = keyboard_low_library[int(file_data[i][1] - 1)]
                    else:
                        target_left = self.angles
                # for right hand
                if file_data[i][2] == 0:
                    if file_data[i+1][2] == 0:
                        target_right = self.angles
                    else:
                        target_right = keyboard_high_library[int(file_data[i+1][2] - 1)]
                else:
                    if file_data[i-1][2] == 0:
                        target_right = keyboard_low_library[int(file_data[i][2] - 1)]
                    else:
                        target_right = self.angles
                target = list(target_left[0:6]) + list(target_right[6:11])
                command_list += self.make_a_move(target, 0.1, 0.06)

                # for the second half cycle, 0.1s
                # for left hand
                if file_data[i][1] == 0:
                    if file_data[i+1][1] == 0:
                        target_left = self.angles
                    else:
                        target_left = keyboard_high_library[int(file_data[i+1][1] - 1)]
                else:
                    if file_data[i+1][1] == 0:
                        target_left = keyboard_high_library[int(file_data[i][1] - 1)]
                    else:
                        target_left = self.angles
                # for right hand
                if file_data[i][2] == 0:
                    if file_data[i+1][2] == 0:
                        target_right = self.angles
                    else:
                        target_right = keyboard_high_library[int(file_data[i+1][2] - 1)]
                else:
                    if file_data[i+1][2] == 0:
                        target_right = keyboard_high_library[int(file_data[i][2] - 1)]
                    else:
                        target_right = self.angles
                target = list(target_left[0:6]) + list(target_right[6:11])
                command_list += self.make_a_move(target, 0.1, 0.06)

        # move to initial position
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list

    def play_music(self, path='./data/music/mother'):
        command_list = list()

        # read file and reformat as a list
        file_data = self.read_reformat_file(path)
        file_data = self.reformat_music_data(file_data)

        # define and move to initial position
        command_list += self.make_a_move(self.initial_position, 2)
        command_list += self.make_a_move(self.music_initial, 2)

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
                    if file_data[i+1][1] == 0:
                        try:
                            if file_data[i+2][1] == 0:
                                target_left = self.angles
                            else:
                                target_left = (np.array(self.angles) +
                                               3 * np.array(keyboard_high_library[int(file_data[i+2][1])])) / 4
                        except IndexError:
                            target_left = self.angles
                    else:
                        target_left = keyboard_high_library[int(file_data[i+1][1])]
                else:
                    if file_data[i-1][1] == 0:
                        target_left = keyboard_low_library[int(file_data[i][1])]
                    elif file_data[i+1][1] == 0:
                        target_left = keyboard_high_library[int(file_data[i][1])]
                    else:
                        target_left = self.angles
                # for right hand
                if file_data[i][2] == 0:
                    if file_data[i+1][2] == 0:
                        try:
                            if file_data[i+2][2] == 0:
                                target_right = self.angles
                            else:
                                target_right = (np.array(self.angles) +
                                                3 * np.array(keyboard_high_library[int(file_data[i+2][2]) + 1])) / 4
                        except IndexError:
                            target_right = self.angles
                    else:
                        target_right = keyboard_high_library[int(file_data[i+1][2]) + 1]
                else:
                    if file_data[i-1][2] == 0:
                        target_right = keyboard_low_library[int(file_data[i][2]) + 1]
                    elif file_data[i+1][2] == 0:
                        target_right = keyboard_high_library[int(file_data[i][2]) + 1]
                    else:
                        target_right = self.angles
                target = list(target_left[0:6]) + list(target_right[6:11])
                if i == 0:
                    command_list += self.make_a_move(target, 0.5, 0.08)
                else:
                    command_list += self.make_a_move(target, 0.15, 0.08)

        # move to initial position
        command_list += self.make_a_move(self.initial_position, 2)
        return command_list

    def get_arm_position(self, temp):
        # transform to -pi - pi. the sign is based on mechanical mounting method
        angles = [0, self.angle_ratio*(2048-temp[1]), self.angle_ratio*(2048-temp[3]),
                  self.angle_ratio*(2048-temp[5]), self.angle_ratio*(2048-temp[7]), 0,
                  self.angle_ratio*(temp[9]-2048), self.angle_ratio*(2048-temp[11]),
                  self.angle_ratio*(temp[13]-2048), self.angle_ratio*(2048-temp[15]), 0]
        return angles

    def record_data(self):
        # this function keep
        file_w = file(self.path, 'w')
        while self.record_flag:
            # this loop keeps running until 'record_flag' is set to be False
            temp_angle = self.current_angles
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

    def go_to_a_point(self, target):
        goal_angle = self.robot.random_sample_ik(target, self.angles)
        if goal_angle is not None:
            trajectory = self.make_a_move(goal_angle, 2)
        else:
            trajectory = self.make_a_move(self.angles, 0.5)
        return trajectory

    def create_control_data(self, data):
        trajectory = None
        if data[0] == 1:
            # update current angle
            # self.angles = self.current_angles
            trajectory = self.make_a_move(self.initial_position, 2)
        elif data[0] == 2:
            trajectory = self.follow_trajectory()
        elif data[0] == 3:
            trajectory = self.begin_record_pose()
        elif data[0] == 4:
            self.angles = self.current_angles
            trajectory = self.stop_record_pose()
        elif data[0] == 5:
            # play two hand music
            trajectory = self.play_music()
        elif data[0] == 6:
            # move to certain angles
            trajectory = self.make_a_move(data[1:12], 2)
        elif data[0] == 7:
            # set pid to initial
            trajectory = self.set_pid_to_default()
        elif data[0] == 10:
            # just do nothing
            trajectory = self.make_a_move(self.angles, 1)
        elif data[0] == 11:
            # return to close position
            trajectory = self.make_a_move(self.half_fold_position, 2)
            trajectory += self.make_a_move(self.fold_position, 2)
        elif data[0] == 12:
            trajectory = self.make_a_move(self.half_fold_position, 2)
            trajectory += self.make_a_move(self.initial_position, 2)
        elif data[0] == 13:
            trajectory = self.make_a_move(self.half_fold_position, 5)
        elif data[0] == 14:
            trajectory = self.make_a_move(self.initial_position, 2)
        elif data[0] == 15:
            trajectory = self.make_a_move(self.fold_position, 2)
        elif data[0] == 16:
            trajectory = self.go_to_a_point(data[1:4])
        return trajectory






















