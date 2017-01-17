# coding=utf-8
# Author: Haotian Shi, Last Modified Date: 2016-02-17
import time

import components.Components as Components
from library.vision.AI_models.voice_ai import voice_ai


class DefaultControl(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)

    def _node_run(self):
        print "default control started..."

        time.sleep(0.2)

        while self.thread_active:

            # 1 get data
            messages = self.get_messages_from_all_topics()

            # if len(messages) > 0:
            #     print "messages in DC", messages

            if messages != []:
                print 'default_control', messages
            # 2 process data
            commands, types, priorities = self.generate_commands_from_messages(messages)

            # 3 output data if necessary
            # if commands != []:
            #     print(commands)
            self.output_all_messages(commands, True)

            # 4 report to master
            self.output_status_to_master(False)

            time.sleep(0.01)

        print "default control closed"

    def generate_commands_from_messages(self, messages):
        # init data storage
        commands = []
        types = []
        priorities = []

        for message in messages:
            command, command_type, message_priority = self.generate_command(message)
            if command is not None:
                commands.append(command)
                types.append(command_type)
                priorities.append(message_priority)

        return commands, types, priorities

    def generate_command(self, message):

        message_type_id = message[1]
        message_data = message[2]
        message_priority = message[3]

        # if command if detected
        if 30 < message_type_id < 40:
            return message_data, message_type_id, message_priority

        command, command_type = {

            2: self.arm_ai,
            3: self.wheel_ai,
            5: voice_ai
            # to be continued
            # .......
        }.get(message_type_id)(message_data)
        return command, command_type, message_priority

    def arm_ai(self, data):
        # takes ui wheel input and transfer it to command format
        command = data
        command_type = "arm_command"
        command = self.message_object.message_warp("arm_command", command)
        return command, command_type

    def wheel_ai(self, data):
        # takes ui wheel input and transfer it to command format
        command = data
        command_type = "wheel_command"
        command = self.message_object.message_warp("wheel_command", command)
        return command, command_type

if __name__ == '__main__':
    master = Components.Master()
    AI = DefaultControl(master)


