# coding=utf-8
import time

from components import Components
from library.vision.AI_models.voice_ai import voice_ai


class AI(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)
        self.command_type = ["control_data", "arm_command", "wheel_command",
                             "cloud_deck_command", "voice_command", "light_command"]
        self.num_class_command = len(self.command_type)

    def _node_run(self):
        print "AI started..."

        while self.thread_active:
            time.sleep(0.05)
            # timer = self.start_time_marker()

            # 1. get data and generate commands
            # print "AI gets  message from topics..."
            commands, types, priorities = self.generate_commands_from_messages()

            # 2. sort them into de-coupled command classes
            # 3. for each command class, get the final message by priority
            # 4. output decision to according topic one by one, pop mechanism.
            # print "AI generates command from messages..."
            self.sort_and_output_commands(commands, types, priorities)

        print "AI closed"

    def generate_commands_from_messages(self):
        topic_length = len(self.topics_in)
        commands = []
        types = []
        priorities = []
        for i in range(topic_length):
            # print "enter loop"
            # get message from different topics
            # assume that there is only two nodes in one topic
            message = self.get_message_from_topic(self.topics_in[i])[0]
            if message is None:
                continue
            # process messages
            # todo: check time_marker here for obsolete messages
            command, command_type, message_priority = self.generate_command(message)
            if command is not None:
                commands.append(command)
                types.append(command_type)
                priorities.append(message_priority)
            # clean topic data
            self.topics_in[i].clean_topic_messages()
            # generate commands
        return commands, types, priorities

    def generate_command(self, message):

        message_type_id = message[1]
        message_data = message[2]
        message_priority = message[3]

        command, command_type = {
            1: self.control_ai,
            2: self.arm_ai,
            3: self.wheel_ai,
            5: voice_ai
            # to be continued
            # .......
        }.get(message_type_id)(message_data)
        return command, command_type, message_priority

    def control_ai(self, data):
        # ai interacts with master
        command_type = "control_data"
        command = data
        return command, command_type

    def arm_ai(self, data):
        # takes ui wheel input and transfer it to command format
        command = data
        command_type = "arm_command"
        return command, command_type

    def wheel_ai(self, data):
        # takes ui wheel input and transfer it to command format
        command = [1, data[0], data[1], 0, 0]
        command_type = "wheel_command"
        return command, command_type

    def sort_and_output_commands(self, commands, types, priorities):
        report_control_data = True

        # loop over the class loop
        for i in range(self.num_class_command):

            target_type = self.command_type[i]
            target_pos = self.find_all_index(types, target_type)
            length_pos = len(target_pos)
            # output not found for this class
            if length_pos < 1:
                continue
            # only one output is found for this class
            elif length_pos == 1:
                self.message_object.message_warp(target_type, commands[target_pos[0]])
                print "Out target:", commands[target_pos[0]]
                self.output_message_to_topic(report_control_data)
            # multiple outputs exists for this class
            else:
                command_potential = []
                # make tuples
                for j in range(length_pos):
                    pos = target_pos[j]
                    command_potential.append((commands[pos], priorities[pos]))
                # sort tuples by priority
                sorted_list = sorted(command_potential, key=lambda t: t[1])
                # get final command
                priority_command = sorted_list[0][0]
                self.message_object.message_warp(target_type,priority_command)
                self.output_message_to_topic(report_control_data)

    def find_all_index(self, array_list, item):
        return [i for i, a in enumerate(array_list) if a == item]


def find_all_index(array_list, item):
    return [i for i,a in enumerate(array_list) if a == item]

if __name__ == '__main__':
    master = Components.Master()
    AI = AI(master)

    data = [100, 5]
    msg = [0, 3, data, "A"]
    print AI.generate_command(msg)
    types = [34, 31]
    p = [1,1]

    # AI.sort_and_output_commands(data, types, p)

    kkk = ["arm_command", "wheel_command", "cloud_deck_command", "voice_command", "light_command"]
    for i in range(len(kkk)-1,0,-1):
        print kkk[i]

    index = kkk.index("arm_command")
    del kkk[index]

    print kkk + [123,23]

    print kkk

    kkk = []
    a = [1]
    b = [2,3]
    kkk.append(a)
    kkk.append(b)
    print kkk
    print "test:", kkk.count("X")
    kkk = [(100,"A"),(200,"C"),(150,"B")]
    x = sorted_list=sorted(kkk, key=lambda t:t[1])
    print x[0][0]

