# Author: Yehang Liu, Last Modified data: 2016-02-18

# contains the methods will not be used in current system as legacy

import serial

# legacies

def _control_data_list(self, control_data):
    command_type = {

        21: self.start_train_new_person_system,
        22: self.stop_train_new_person_system,
        24: self.start_test_roam,
        25: self.stop_test_roam,
        26: self.start_cloud()
        # to be continued
    }.get(control_data)
    return command_type


def update_node_and_link(self, node, commands):
    # command list:
    # command[0] is command type: open  /   kill            /   pause       /   restart
    # command[1] is node type txt       /   node_name       /   node_name   /   node_name
    # command[2] is node name           /   topic_name      /   None        /   None
    # command[3]: input/output/bothway  /   topic_name_sec  /   None        /   None
    # command[4] topic name 1           /   None            /   None        /   None
    # command[5] topic name 2 (if has)  /   None            /   None        /   None
    # if the input is a single command, please add [] outside the command
    # if use any of open ... please put open command as the first command
    for i in range(0, len(commands)):
        command = commands[i]
        type = command[0]
        # length = len(command)
        if type is 'open':
            node_type = command[1]
            node_name_new = command[2]
            direction = command[3]
            topic_name_new = command[4]
            self.add_node(node_type, node_name_new)
            if direction is 'input':
                self.add_topic(topic_name_new)
                self.link_node_topic(node_name_new, topic_name_new, 'input_of_node')
                self.link_node_topic(node, topic_name_new, 'output_of_node')
            elif direction is 'output':
                self.add_topic(topic_name_new)
                self.link_node_topic(node, topic_name_new, 'input_of_node')
                self.link_node_topic(node_name_new, topic_name_new, 'output_of_node')
            elif direction is 'bothway':
                topic_name_sec_new = command[5]
                self.add_topic(topic_name_new)
                self.add_topic(topic_name_sec_new)
                self.link_node_topic(node_name_new, topic_name_new, 'input_of_node')
                self.link_node_topic(node, topic_name_new, 'output_of_node')
                self.link_node_topic(node_name_new, topic_name_sec_new, 'output_of_node')
                self.link_node_topic(node, topic_name_sec_new, 'input_of_node')

        elif type is 'kill':
            node_name_kill = command[1]
            topic_name_kill = command[2]
            self.del_topic(topic_name_kill)
            self.del_node(node_name_kill)
            if len(command) is 4:
                topic_name_sec_kill = command[3]
                self.del_topic(topic_name_sec_kill)
        elif type is 'pause':
            node_name_target = command[1]
            try:
                index_pos = self.all_nodes_name.index(node_name_target)
            except ValueError:
                print('no this node')
                return
            self.all_nodes_name[index_pos].stop_thread()
        elif type is 'restart':
            node_name_target = command[1]
            try:
                index_pos = self.all_nodes_name.index(node_name_target)
            except ValueError:
                print('no this node')
                return
            self.all_nodes_name[index_pos].thread_active = True


def init_topic_and_link(self, node, node_sec, topic_name, direction, topic_name_sec=None):
    self.add_topic(topic_name)
    if direction is 'input':
        self.link_node_topic(node, topic_name, 'input_of_node')
        self.link_node_topic(node_sec, topic_name, 'output_of_node')
    elif direction is 'output':
        self.link_node_topic(node, topic_name, 'output_of_node')
        self.link_node_topic(node_sec, topic_name, 'input_of_node')
    elif direction is 'bothway':
        self.add_topic(topic_name_sec)
        self.link_node_topic(node, topic_name, 'input_of_node')
        self.link_node_topic(node_sec, topic_name, 'output_of_node')
        self.link_node_topic(node, topic_name_sec, 'output_of_node')
        self.link_node_topic(node_sec, topic_name_sec, 'input_of_node')


def test_arm(master):
    # ser_arm = serial.Serial("/dev/arduino011", baudrate=115200, timeout=None)
    ser_arm = serial.Serial("/dev/ttyACM1", baudrate=115200, timeout=None)
    master.add_node('serial_transmit', 'arm_serial', [ser_arm, 21, 20, "arm_head"])
    master.add_topic('arm_control_to_arm_serial', ['arm_to_serial'])
    master.link_node_topic('arm_serial', 'arm_control_to_arm_serial', 'input_of_node')

    master.add_node('arm_node', 'arm_control')
    master.add_topic('decision_tree_to_arm_control', ['arm_command'])
    master.link_node_topic('arm_control', 'arm_control_to_arm_serial', 'output_of_node')
    master.link_node_topic('arm_control', 'decision_tree_to_arm_control', 'input_of_node')

    master.add_topic('arm_serial_to_arm_control', ['arm_head'])
    master.link_node_topic('arm_control', 'arm_serial_to_arm_control', 'input_of_node')
    master.link_node_topic('arm_serial', 'arm_serial_to_arm_control', 'output_of_node')


def test_wheel(master):
    ser_wheel = serial.Serial("/dev/arduino021", baudrate=115200, timeout=None)
    master.add_node('serial_transmit', 'wheel_serial', [ser_wheel, 8, 14, "wheel_imu_sonar"])
    master.add_topic('topic_wheel_to_serial', ['wheel_to_serial'])
    master.link_node_topic('wheel_serial', 'topic_wheel_to_serial', 'input_of_node')

    master.add_node('wheel_node', 'wheel_control')
    master.add_topic('decision_tree_to_wheel_control', ['wheel_command'])
    master.link_node_topic('wheel_control', 'topic_wheel_to_serial', 'output_of_node')
    master.link_node_topic('wheel_control', 'decision_tree_to_wheel_control', 'input_of_node')

    # add sensor
    master.add_node('sensor_listener', 'sensor_listener')
    master.add_topic('topic_wheel_serial_to_sensor_listener', ['wheel_imu_sonar'])
    master.link_node_topic('sensor_listener', 'topic_wheel_serial_to_sensor_listener', 'input_of_node')
    master.link_node_topic('wheel_serial', 'topic_wheel_serial_to_sensor_listener', 'output_of_node')

    master.add_topic('topic_sensor_listener_to_wheel_node', ['robot_position'])
    master.link_node_topic('wheel_control', 'topic_sensor_listener_to_wheel_node', 'input_of_node')
    master.link_node_topic('sensor_listener', 'topic_sensor_listener_to_wheel_node', 'output_of_node')

