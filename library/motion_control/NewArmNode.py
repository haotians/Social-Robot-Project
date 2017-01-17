# this class is used to listen and record
import time

import components.Components
import NewArmControlClass
import HeadControlClass


class ArmNode(components.Components.Node):

    def __init__(self, master_object):
        components.Components.Node.__init__(self, master_object)
        self.name = 'arm_control'
        self.head_object = HeadControlClass.HeadControlClass()
        self.arm_object = NewArmControlClass.ArmControlClass()

    def _node_run(self):

        print 'arm sys started'
        time.sleep(0.5)

        while self.thread_active:

            # Part 1: read all message:
            messages = self.get_messages_from_all_topics()

            # Part 2: use these messages to generate commands for each topic

            # Part 2.1: preprocess data, get command for wheel
            current_time = time.time()
            arm_command = None
            head_command = None
            for i in range(len(messages)):
                if messages[i] is not None:
                    msg_time, msg_type, data, source = self.message_object.message_dewarp(messages[i])
                    if msg_type == 31:
                        arm_command = data[0:10]
                        head_command = data[10:13]
                        # print "arm_command", data
                    if msg_type == 92:
                        arm_data = data[0:17]
                        self.arm_object.current_angles = self.arm_object.output_to_radius(arm_data)
            # todo: ArmControlClass need feedback from serial port
            # Part 2.2 generate commands
            if arm_command is not None:
                raw_arm_commands = self.arm_object.create_control_data(arm_command)
                raw_head_commands = self.head_object.create_control_data(head_command)
                whole_commands = list()
                length_arm = len(raw_arm_commands)
                length_head = len(raw_head_commands)
                if length_arm == length_head:
                    for i in range(length_arm):
                        temp_command = raw_arm_commands[i] + raw_head_commands[i]
                        whole_commands.append(temp_command)
                else:
                    for i in range(length_arm):
                        temp_command = raw_arm_commands[i] + raw_head_commands[0]
                        whole_commands.append(temp_command)
                commands = [self.message_object.message_warp("arm_to_serial", whole_commands)]
                # print(commands)
            else:
                commands = [self.message_object.message_warp("no_command", [0])]

            # Part 3: output command
            self.output_all_messages(commands)

            # Part 4: report to master
            self.output_status_to_master(False)
            # this sleep time can not be too large, due to the control cycle limit of arduino
            time.sleep(0.01)

