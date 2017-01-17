# coding=utf-8
# Author: Haotian Shi, Last Modified Date: 2016-02-17
import time

from components import Components

TimeTolerance = 20

class DecisionTree(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)
        self.master_confirmation_flag = False

    def _node_run(self):
        print "DT started..."

        while self.thread_active:
            # 1 get data
            messages, control_data = self.get_messages_and_control_data()

            # 2 process data
            self.communicate_with_master(control_data)

            # 3 output data if necessary
            self.output_all_messages(messages, False)

            # 4 report to master
            self.output_status_to_master(False)

            time.sleep(0.01)


        print "DT closed..."

    def get_messages_and_control_data(self):
        control_data = []
        messages = self.get_messages_from_all_topics()
        if len(messages) >  1:
            print messages
        for message in messages:
            # protect invalid message
            if message is None:
                continue
            else:
                msg_type = message[1]
                # control_data type, need to be extract here
                if msg_type == 1:
                    control_data.append(message)
                # todo: maybe we should pass messages_none_control instead of messages
                # todo: we have to think, is it necessary to pass control data to app?
        return messages, control_data

    def communicate_with_master(self, control_data):
        for command in control_data:

            self.message_object.message = command
            self.set_master_confirmation_status(False)
            self.output_status_to_master(True)

            timer0 = time.time()

            # if master hasn't confirmation in 20s, command is considered processed successfully
            while not self.master_confirmation_flag or time.time() - timer0 > TimeTolerance:
                time.sleep(0.01)
                continue

            print "Master confirmed to DT command: ", command, " is done"

            self.set_master_confirmation(False)

    def set_master_confirmation_status(self, status):
        self.master_confirmation_flag = status

    def route_message_to_topics(self, messages):
        for message in messages:
            if message is None:
                continue
            # load the message
            self.message_object.message = message
            # shot the message through the router
            self.output_all_messages(message)


def find_all_index(array_list, item):
    return [i for i, a in enumerate(array_list) if a == item]

if __name__ == '__main__':
    # test = [['open', 'app_train_face', 'train_face', 'bothway', 'topic_dt2face_train', 'topic_face_train2dt']]
    # test2 = [['open', 'app_train_face', 'train_face', 'bothway', 'topic_dt2face_train', 'topic_face_train2dt']]
    # name = 'a'
    # sen = name+',你好'
    # test3 = test.append(test2)
    # import copy
    # a = [1,4,6]
    # b = copy.copy(a)
    # a[1] = 15
    # print b
    # m = {
    #     1:'xxx',
    #     2:'yyy'
    # }
    #
    # m2 = dict(map(lambda t:(t[1],t[0]), m.items()))
    # m2 = m.get(1)
    # a = 1
    # # if type(a) is int:
    #   print a
    a = []
    a.append(['b',1,1])
    a.append(['ab',1,1])
    b = a[0][2]
    if 'b' in a[0]:
        print type(a), type(b)




