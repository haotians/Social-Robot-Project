# Author: Yehang Liu, Last Modified Date: 2016-02-19
# this class is used to listen and record
import time
import numpy as np
from scipy import constants

from socketIO_client import SocketIO
from socketIO_client import LoggingNamespace as lognamespace

import components.Components

SERVER = '123.57.176.245'
PORT = 80


class SensorListener(components.Components.Node):

    def __init__(self, master_object):
        components.Components.Node.__init__(self, master_object)
        self.name = 'sensor_listener'

        # arm
        # build a data list with cursor
        self.arm_data = []
        self.arm_cursor = 0
        # file name to save data
        self.arm_data_file = None

        # wheel
        # build a data list with cursor
        self.wheel_data = []
        self.wheel_cursor = 0
        # file name to save data
        self.wheel_data_file = None

        # imu and sonar
        # build a data list with cursor
        self.imu_and_sonar_data = []
        self.imu_and_sonar_cursor = 0
        # file name to save data
        self.imu_and_sonar_data_file = None

        # robot position, [x, y, theta]
        self.current_position = [0, 0, 0]
        self.current_position_imu = [0, 0, 0]

        # robot wheel position, only used for save last position
        self.wheel_position = [None, None]

        # max data length
        self.max_data_length = 200

        self.sleep_time = 0.03

    def __del__(self):
        self.stop_thread()
        if self.arm_data_file is not None:
            self.arm_data_file.close()
        if self.wheel_data_file is not None:
            self.wheel_data_file.close()
        if self.imu_and_sonar_data_file is not None:
            self.imu_and_sonar_data_file.close()

    def insert_data_to_list(self, data, data_list, cursor_position):
        # data_list store recent max_data_length data. cursor_position shows the most recent data

        if len(data_list) < self.max_data_length:
            # if data_list is short, just append
            data_list.append(data)
            cursor_position += 1

        elif len(data_list) == self.max_data_length:
            # if data_list is long, delete oldest data and insert newest
            if cursor_position == self.max_data_length:
                cursor_position = 1
            else:
                cursor_position += 1
            del data_list[cursor_position - 1]
            data_list.insert(cursor_position - 1, data)
        return data_list, cursor_position

    def calculate_current_position(self, previous_position, wheel_move):
        delta = self.calculate_delta_position(wheel_move)

        current_position = [0, 0, 0]
        matrix = self.homo_trans_matrix(previous_position[0], previous_position[1], previous_position[2])
        homo_position = matrix.dot(np.array([delta[0], delta[1], 1]))
        current_position[0] = homo_position[0]
        current_position[1] = homo_position[1]
        current_position[2] = previous_position[2] + delta[2]

        # the angle should be in the range of -pi -- pi
        while current_position[2] <= -constants.pi:
            current_position[2] += 2 * constants.pi
        while current_position[2] > constants.pi:
            current_position[2] -= 2 * constants.pi

        return current_position

    def homo_trans_matrix(self, x, y, theta):
        matrix = np.array([[np.cos(theta), -np.sin(theta), x],
                           [np.sin(theta), np.cos(theta), y],
                           [0, 0, 1]])
        return matrix

    def calculate_delta_position(self, wheel_move):
        delta = [0, 0, 0]
        l = 0.1648
        if wheel_move[0] == wheel_move[1]:
            # straight
            delta[0] = wheel_move[0]
        else:
            radius = l * (wheel_move[0] + wheel_move[1]) / (wheel_move[1] - wheel_move[0])
            angle = (wheel_move[1] - wheel_move[0]) / (2 * l)

            delta[0] = radius * np.sin(angle)
            delta[1] = radius * (1 - np.cos(angle))
            delta[2] = angle
        return delta

    def calculate_delta_position_with_imu(self, wheel_move, imu_diff):
        delta = [0, 0, 0]
        distance = (wheel_move[0] + wheel_move[1]) / 2
        delta[2] = imu_diff
        delta[0] = distance * np.cos(imu_diff)
        delta[1] = distance * np.sin(imu_diff)
        return delta

    def calculate_current_position_with_imu(self, previous_position, wheel_move, imu_diff):
        delta = self.calculate_delta_position_with_imu(wheel_move)

        current_position = [0, 0, 0]
        matrix = self.homo_trans_matrix(previous_position[0], previous_position[1], previous_position[2])
        homo_position = matrix.dot(np.array([delta[0], delta[1], 1]))
        current_position[0] = homo_position[0]
        current_position[1] = homo_position[1]
        current_position[2] = previous_position[2] + imu_diff
        return current_position

    def raw_data_to_metric_data(self, wheel_data):
        # this method change units from switch_times, switch_frequency, switch_frequency/s to m, m/s, m/s^2
        # for one round, 1200 switch times. So 1 round/s = 1200 Hz. 1 round/s^2 = 1200 Hz/s
        switch_per_round = 1200
        # the diameter of the wheel is 0.152 m, so the perimeter is pi * 0.152 = 0.477 m
        perimeter = 0.495
        wheel_move = [0, 0]
        # print "wheel_data:", wheel_data
        for i in range(2):
            temp_low = wheel_data[4*i]
            temp_high = wheel_data[4*i+1]
            temp_wheel_position = 65536 * temp_high + temp_low
            if temp_wheel_position > 2147483648:
                temp_wheel_position -= 4294967296
            temp_wheel_position = temp_wheel_position * perimeter / switch_per_round
            if self.wheel_position[i] is None:
                wheel_move[i] = 0
            else:
                wheel_move[i] = temp_wheel_position - self.wheel_position[i]
            self.wheel_position[i] = temp_wheel_position
        return wheel_move

    def save_data(self, data, file_name):
        # save data
        temp_str = ''
        for i in data:
            temp_str += str(i)
            temp_str += ' '
        temp_str += '\n'
        file_name.writelines(temp_str)
        file_name.flush()

    def _node_run(self):

        print 'sensor sys has been started\n'

        time.sleep(1)

        # socketIO = SocketIO(SERVER, PORT, lognamespace)
        current_time = time.time()
        # open files
        path = './data/sensor_data/arm' + str(int(current_time))
        self.arm_data_file = file(path, 'w')

        path = './data/sensor_data/wheel' + str(int(current_time))
        self.wheel_data_file = file(path, 'w')

        path = './data/sensor_data/imu_and_sonar' + str(int(current_time))
        self.imu_and_sonar_data_file = file(path, 'w')

        temp_count = 0
        while self.thread_active:

            # Part 1: read all message:
            messages = self.get_messages_from_all_topics()

            # Part 2: use these messages to generate commands for each topic

            # Part 2.1: preprocess data, get arm, wheel, imu, sonar data
            current_time = time.time()
            wheel_data = None
            arm_data = None
            imu_and_sonar_data = None
            commands_to_UI = None
            for i in range(len(messages)):
                if messages[i] is not None:
                    # print('sensor_data')
                    # print(messages[i])
                    msg_time, msg_type, data, source = self.message_object.message_dewarp(messages[i])
                    if msg_type == 91:
                        wheel_data = data[1:9]
                        imu_and_sonar_data = data[9: 15]
                    elif msg_type == 92:
                        arm_data = data[1:9]

            # Part 2.2: calculate current position
            if wheel_data is not None:
                wheel_move = self.raw_data_to_metric_data(wheel_data)
                self.current_position = self.calculate_current_position(self.current_position, wheel_move)
                if temp_count < 20:
                    temp_count += 1
                else:
                    # socketIO.emit('message', str((150-50*self.current_position[1], 150-50*self.current_position[0])))

                    # generate message for UI to display the position and trajectory of wheel's motion

                    position_info = str((150-50*self.current_position[1], 150-50*self.current_position[0]))
                    commands_to_UI = self.message_object.message_warp('position_on_UI', position_info, 'sensor_listener')
                    temp_count = 0

            # Part 2.3: save data
            if arm_data is not None:
                temp_data = arm_data
                temp_data.insert(0, current_time)
                self.arm_data, self.arm_cursor = self.insert_data_to_list(temp_data, self.arm_data, self.arm_cursor)
                self.save_data(temp_data, self.arm_data_file)

            if wheel_data is not None:
                temp_data = wheel_data
                temp_data.insert(0, current_time)
                self.wheel_data, self.wheel_cursor = self.insert_data_to_list(temp_data, self.wheel_data,
                                                                              self.wheel_cursor)
                self.save_data(temp_data, self.wheel_data_file)

            if imu_and_sonar_data is not None:
                temp_data = imu_and_sonar_data
                temp_data.insert(0, current_time)
                self.imu_and_sonar_data, self.imu_and_sonar_cursor = self.insert_data_to_list(temp_data,
                                                                                              self.imu_and_sonar_data,
                                                                                              self.imu_and_sonar_cursor)
                self.save_data(temp_data, self.imu_and_sonar_data_file)

            # Part 2.4: generate commands
            commands = []
            commands.append(self.message_object.message_warp("robot_position", self.current_position, "sensor_listener"))
            if imu_and_sonar_data is not None:
                commands.append(self.message_object.message_warp("sonar_distance", imu_and_sonar_data[2:7]))
                # print 'sonar:', imu_and_sonar_data

            # insert information of robot's current position into the message list

            if commands_to_UI is not None:
                commands.append(commands_to_UI)

            # print "sensor data: ", commands
            # Part 3: output commands
            self.output_all_messages(commands)

            # Part 4: report to master
            self.output_status_to_master(False)
            # this sleep time can not be too large, due to the control cycle limit of arduino
            time.sleep(self.sleep_time)
