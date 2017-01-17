# Author: Haotian Shi, Last Modified Date: 2016-02-17
# Author: Yehang Liu, Last Modified Date: 2016-02-17
#  define the basic components for robotic system
# it's a simplification of ROS
import time
import threading
import copy


# message stands for the information that node sends/receives
class Message(object):
    def __init__(self):
        # message should be in the form of [time_marker, message_type, data, source_type]
        self.message = None

    def _generate_source_type_id(self, source_text):
        # should introduce try-catch mechanism for invalid type_text
        value = {
            "null": 0,
            "ui": 1,
            "voice": 2,
            "vision": 3,
            "train_face": 4,
            "sensor_listener": 5,
            # to be continued
            # .......
        }

        if type(source_text) is int:
            value = dict(map(lambda t:(t[1],t[0]), value.items()))
        return value.get(source_text)

    def _generate_message_type_id(self, type_text):
        # to do:_
        # should introduce try-catch mechanism for invalid type_text
        value = {

            # control_data: the only data type that may pass from node to master,
            # which controls the activity of all the threads in the master

            # 0 NULL report to master

            # 1 camera off
            # 2 camera on local only
            # 3 camera on web only
            # 4 camera on local and web
            # 5 kill vision system

            # 1 kill vision system
            # 2 camera on local only
            # 3 camera on web only
            # 4 camera on local and web
            # 5 start marker app
            # 6 start emotion detect
            # 7 training new person for local face
            # 8 start obeject recognition

            # 11 voice off
            # 12 voice on web
            # 13 voice on local
            # 14 listen on
            # 15 listen off

            # 21 training new person for local face
            # 22 finish training new person and end process
            # 23 start track app
            # 24 stop track app
            # 25 start roam app
            # 26 stop roam app
            # 27 start cloud app
            # 29 start marker app
            # 30 stop marker app
            # 31 start emotion detect
            # 32 stop emotion detect

            "control_data": 1,
            "arm_data": 2,
            "wheel_data": 3,
            "cloud_deck_data": 4,
            "voice_data": 5,

            # temp use for demo 02 04 2016
            # 0 listen on, 1 listen off

            "listen_on_off": 300,

            "arm_command": 31,
            "wheel_command": 32,
            "cloud_deck_command": 33,
            "voice_command": 34,
            "light_command": 35,

            # type in 40s will be assigned to display Robot's status on UI

            "position_on_UI": 41,

            "train_face": 61,
            "distance_data": 62,
            "vision": 63,

            "robot_position": 71,
            "sonar_distance": 72,

            "wheel_to_serial": 81,
            "arm_to_serial": 82,
            "wheel_move_stage": 83,

            "wheel_imu_sonar": 91,
            "arm_head": 92,

            "for_marker": 93,

            "no_command": 99,

            # "ui_input_command": 11,
            # "aud_control": 13

            # to be continued
            # .......
        }.get(type_text)
        return value

    def message_warp(self, type_text, message_data,  source_text = "null"):
        message_type = self._generate_message_type_id(type_text)
        source_type = self._generate_source_type_id(source_text)
        time_marker = time.time()
        message = [time_marker, message_type, message_data, source_type]
        return message

    def message_dewarp(self, message):
        # [time_marker, message_type, data, source_type]
        return message[0], message[1], message[2], message[3]

    # seems not useful in the system since node data won't be accessed by other nodes
    def clean_message(self):
        self.message = None


# basic structure node
# node stands for every possible thread that may exists in the robotic system
class Node(object):
    def __init__(self, master_object=None):
        # init its master
        self.master = master_object
        # node ID in master level
        self.master_register_id = None
        # init message
        self.message_object = Message()
        # thread control
        self.thread_active = False
        # node/topic linked
        # input topic
        self.topics_in = []
        # output topic
        self.topics_out = []
        # node name
        self.name = 'raw_node'
        # node thread
        self.node_thread = None
        # store the valid msg types for each output topic that links to this node
        self.topics_out_valid_types = []
        # message type lock
        self.out_message_type_lock = []

        # todo: need to add several methods to check input/output type
        # possible input/output
        self.possible_input = [98]
        self.possible_output = [98]

    def set_master_confirmation(self, status):
        self.master_confirmation_flag = status

    def update_out_message_type_lock(self, new_lock):
        self.out_message_type_lock = new_lock

    def update_topics_out_valid_types(self, valid_types):
        valid_types_id = []
        for i in range(len(valid_types)):
            id = self.message_object._generate_message_type_id(valid_types[i])
            valid_types_id.append(id)
        # put valid types for certain topic in node by time sequence
        self.topics_out_valid_types.append(valid_types_id)

    def change_node_name(self, text):
        self.name = text

    # set node ID, not used
    def set_node_id(self, id_in_master):
        self.master_register_id = id_in_master

    # return nodeID, not used
    def get_node_id(self):
        return self.master_register_id

    # thread switch
    def start_thread(self):
        # start thread
        self.node_thread = threading.Thread(target=self._node_run)
        self.node_thread.daemon = True
        self.thread_active = True  # used to stop thread
        self.node_thread.start()  # start thread

    def stop_thread(self):
        self.thread_active = False

    # output input management
    def add_input_topic(self, topic_object):
        # try-catch mechanism for protection
        try:
            index = self.topics_in.index(topic_object)
            print "topic already registered in the node"
        except:
            self.topics_in.append(topic_object)

    def add_output_topic(self, topic_object):
        # try-catch mechanism for protection
        try:
            index = self.topics_out.index(topic_object)
            print "topic already registered in the node"
        except:
            self.topics_out.append(topic_object)
            # add valid msg type
            self.update_topics_out_valid_types(topic_object.valid_message_types)

    def del_input_topic(self, topic_object):
        try:
            index_pos = self.topics_in.index(topic_object)
        except ValueError:
            print('no this topic')
            return
        del self.topics_in[index_pos]

    def del_output_topic(self, topic_object):
        try:
            index_pos = self.topics_out.index(topic_object)
        except ValueError:
            print('no this topic')
            return
        del self.topics_out[index_pos]
        del self.topics_out_valid_types[index_pos]

    # message operation
    def get_message_from_topic(self, topic_object):
        return topic_object.messages

    def get_messages_from_all_topics(self):
        # important, this method will erase the message in topic
        all_messages = []
        # loop over all the input topics
        for topic in self.topics_in:
            # try-catch mechanism for protection
            try:
                messages = self.get_message_from_topic(topic)
                # loop over all the meaasges from one topic
                for one_message in messages:
                    all_messages.append(one_message)
                # todo: in future, we should not clean the topic messages
                topic.clean_topic_message()
            except ValueError:
                continue
        return all_messages

    def output_a_command(self, messages, topic_object):
        topic_object.topic_receive_message(messages)

    def output_all_messages(self, messages, out_put_lock = False):
        # loop all target topics and output message to them
        msg = copy.copy(messages)
        length_topic_output = len(self.topics_out)
        length_messages = len(msg)

        # loop over all the topics
        for i in range(length_topic_output):
            # try-catch mechanism for topic protection, case: while still looping j and length_topic_output changes
            try:
                # get the valid msg type for this topic
                valid_msg_type = self.topics_out_valid_types[i]
                # print valid_msg_type
                if out_put_lock:
                    # print self.topics_out_valid_types, self.out_message_type_lock
                    # check length, if length equals, we know that this app is locked
                    if len(valid_msg_type) == len(self.out_message_type_lock):
                        continue
                    # msg_out
                    msg_out = []
                    # loop over all the topics
                    for j in range(length_messages):
                        message = messages[j]
                        message_type = message[1]
                        # if this topic doesn't support this type of msg or this msg is blocked, continue
                        if valid_msg_type.count(message_type) == 0 or self.out_message_type_lock.count(message_type) > 0:
                            continue
                        else:
                            msg_out.append(message)
                    # output msgs for this topic
                    if len(msg_out) > 0:
                        self.output_a_command(msg_out, self.topics_out[i])
                else:
                    # msg_out
                    msg_out = []
                    # loop over all the topics
                    for j in range(length_messages):

                        message = messages[j]
                        message_type = message[1]
                        # if this topic doesn't support this type of msg or this msg is blocked, continue
                        if valid_msg_type.count(message_type) == 0:
                            continue
                        else:
                            msg_out.append(message)
                    # output msgs for this topic
                    if len(msg_out) > 0:
                        self.output_a_command(msg_out, self.topics_out[i])

            except ValueError:
                continue

    # tell the master that this node has done its job in this iteration
    # if report_control_data is True, msg with type of control_data will be reported to master
    def output_status_to_master(self, report_control_data):
        if report_control_data:
            # get the type
            info_type = self.message_object.message[1]
            # control_data will be directly passed to master for process
            if info_type == 1:
                control_data = self.message_object.message[2]
                self.master.get_status_report(self.name, control_data)
            # normal report
            else:
                self.master.get_status_report(self.name, 0)
        # normal report
        else:
            self.master.get_status_report(self.name, 0)

    # virtual function
    def set_node_status(self, init_parameter):
        # this method is not necessary for most nodes
        pass

    # virtual function
    def do_nothing(self, messages):
        return []

    # virtual function
    def _node_run(self):

        while self.thread_active:
            # for all nodes, the node run should have similar structure.
            # first, read all topic. then process. last, write all topic.
            # we can try to write a template here

            # Part 1: read all message:
            messages = self.get_messages_from_all_topics()

            # Part 2: process msg
            commands = self.do_nothing(messages)

            # Part 3: output all commands
            self.output_all_messages(commands)

            # Part 4: report to master
            self.output_status_to_master(0)
            time.sleep(1)


# basic structure topic
# topic is used to store the output from node so that nodes are de-coupled with each other
# no thread in topic, just a place to place data. (LOL)
# topics only save one topic
class Topic(object):
    def __init__(self, valid_msg_types = None):
        # node name
        self.name = 'raw_topic'
        self.input_nodes = []
        self.messages = []
        self.output_nodes = []
        # topic ID in master level, currently not used
        self.master_register_id = None
        # valid_msg_types is a list that stores the msg type that this topic support
        self.valid_message_types = valid_msg_types

    def change_topic_name(self, text):
        self.name = text

    def add_input_node(self, node):
        self.input_nodes.append(node)

    def add_output_node(self, node):
        self.output_nodes.append(node)

    def del_input_node(self, node):
        try:
            index_pos = self.input_nodes.index(node)
        except ValueError:
            print('no this node')
            return
        del self.input_nodes[index_pos]

    def del_output_node(self, node):
        try:
            index_pos = self.output_nodes.index(node)
        except ValueError:
            print('no this node')
            return
        del self.output_nodes[index_pos]

    def topic_receive_message(self, messages):
        # todo: here, we need to check whether the type of message is correct. this should be easy
        self.messages = messages
        # if self.name == "topic_sensor2roam":
        #     print "sensor data in topic_sensor2roam: ", self.messages

    def clean_topic_message(self):
        # clean all messages in topic
        # maybe need to be modified for a more data-friendly method
        self.messages = []

    # set node ID, currently not used
    def set_topic_id(self, id_in_master):
        self.master_register_id = id_in_master


class Master(object):
    def __init__(self):
        # all node objects and their ID
        self.all_nodes = []
        self.all_nodes_name = []

        self.node_check_list_buffer = []

        # all topics and their ID
        self.all_topics = []
        self.all_topics_name = []

        # app names
        self.all_app_node_names = []

        # app lock, has the same length with app_node_names
        self.apps_resource_list = []
        self.apps_resource_block_list = []

        # node check period
        # to do, this period should be synchronized with AI's decision period
        self.node_check_time = 0.1

        # thread for node status checking
        self.master_thread = None
        self.thread_active = False

        # confirmation name for a node
        self.node_check_name = None
        self.node_check_status = True

    # virtual method
    def create_a_node(self, node_type):
        # implementation should be defined outside Components
        pass

    def add_node(self, node_type, node_name, init_parameter=None, app_output_types=[]):
        # todo: we need to check whether the node name is used

        try:
            index = self.all_nodes_name.index(node_name)
            print "node already in the list"
            return
        except:
            print "node pass check ", node_name

        node_object = self.create_a_node(node_type)
        if init_parameter is not None:
            node_object.set_node_status(init_parameter)
        # update name
        node_object.change_node_name(node_name)
        # update node object list
        self.all_nodes.append(node_object)
        # update node name(ID) list
        self.all_nodes_name.append(node_name)
        # update app node if necessary
        if len(app_output_types) > 0:
            # check node
            if self.all_app_node_names.count(node_name) == 0:
                self.all_app_node_names.append(node_name)
                self.apps_resource_list.append(app_output_types)
                self.update_apps_reource_block_list()
                self.update_all_apps_lock()
        # update check list
        self.node_check_list_buffer.append(-1)
        node_object.start_thread()

    def del_node(self, node_name):
        # when we delete a node, we should check all the input and output topics of this node
        # if there exists a topic which only connected to this node, delete the topic first
        try:
            index_pos = self.all_nodes_name.index(node_name)
        except ValueError:
            print('no this node')
            print "node_name: ", node_name
            return

        # deactive node
        self.all_nodes[index_pos].stop_thread()

        # unlink the node from topic
        for topic in self.all_nodes[index_pos].topics_in:
            # unlink this node with input topics
            self.unlink_node_topic(node_name, topic.name)
        for topic in self.all_nodes[index_pos].topics_out:
            # unlink this node with output topics
            self.unlink_node_topic(node_name, topic.name)

        # update

        # then delete itself
        del self.all_nodes[index_pos]
        del self.all_nodes_name[index_pos]
        del self.node_check_list_buffer[index_pos]

        # if it's an app node, we need to delete it from the app node list
        try:
            index_pos_app_list = self.all_app_node_names.index(node_name)
            del self.all_app_node_names[index_pos_app_list]
        except:
            return

    def add_topic(self, topic_name, valid_msg_types = "None"):
        # todo: we need to check whether the topic name is used
        topic_object = Topic(valid_msg_types)
        topic_object.change_topic_name(topic_name)
        self.all_topics.append(topic_object)
        self.all_topics_name.append(topic_name)

    def del_topic(self, topic_name):
        try:
            index_pos = self.all_topics_name.index(topic_name)
        except ValueError:
            print('no this topic')
            return
        for node in self.all_topics[index_pos].input_nodes:
            # unlink this topic with input node
            self.unlink_node_topic(node.name, topic_name)
        for node in self.all_topics[index_pos].output_nodes:
            # unlink this topic with output node
            self.unlink_node_topic(node.name, topic_name)
        del self.all_topics[index_pos]
        del self.all_topics_name[index_pos]

    # thread switch
    def start_thread(self):
        # start thread
        self.master_thread = threading.Thread(target=self.check_node_status())
        self.master_thread.daemon = True
        self.thread_active = True  # used to stop thread
        self.master_thread.start()  # start thread

    def stop_thread(self):
        self.thread_active = False

    def link_node_topic(self, node_name, topic_name, in_out_type):
        try:
            index_node = self.all_nodes_name.index(node_name)
            index_topic = self.all_topics_name.index(topic_name)
        except ValueError:
            print('no this topic or this node')
            print "name: ", node_name,topic_name
            return
        if in_out_type == 'input_of_node':
            self.all_nodes[index_node].add_input_topic(self.all_topics[index_topic])
            self.all_topics[index_topic].add_output_node(self.all_nodes[index_node])
        elif in_out_type == 'output_of_node':
            self.all_nodes[index_node].add_output_topic(self.all_topics[index_topic])
            self.all_topics[index_topic].add_input_node(self.all_nodes[index_node])

    def unlink_node_topic(self, node_name, topic_name):
        try:
            index_node = self.all_nodes_name.index(node_name)
            index_topic = self.all_topics_name.index(topic_name)
        except ValueError:
            print('no this topic or this node')
            return

        # delete topic information in node
        try:
            self.all_nodes[index_node].topics_in.index(self.all_topics[index_topic])
            self.all_nodes[index_node].del_input_topic(self.all_topics[index_topic])
        except ValueError:
            self.all_nodes[index_node].topics_out.index(self.all_topics[index_topic])
            self.all_nodes[index_node].del_output_topic(self.all_topics[index_topic])

        # delete node information in topic
        try:
            self.all_topics[index_topic].input_nodes.index(self.all_nodes[index_node])
            self.all_topics[index_topic].del_input_node(self.all_nodes[index_node])
        except ValueError:
            self.all_topics[index_topic].output_nodes.index(self.all_nodes[index_node])
            self.all_topics[index_topic].del_output_node(self.all_nodes[index_node])

    # read node report, make according changes to nodes or topics when control_data is detected
    def check_node_status(self):
        # check status loop
        while True:
            # define control_data must be transmitted from DT, one msg each loop
            control_data = None
            # sleep a little bit
            time.sleep(self.node_check_time)
            length_node_active = len(self.all_nodes_name)
            # loop all the active nodes to get there
            node_check_list = copy.copy(self.node_check_list_buffer)

            for i in range(length_node_active):
                status = node_check_list[i]
                # node failed
                if status < 0:
                    # print "failed to read data from node: ",self.active_nodes_id[i]
                    # todo: restart the node
                    pass
                # node working, do nothing
                elif status == 0:
                    continue

                # AI node working and it pass the control_data to master
                else:
                    # erase data
                    print "master find control_data in node: ", self.all_nodes[i].name
                    control_data = status

            # print "active Node: ", self.active_nodes_id
            # process control_data
            if control_data is None:
                continue
            else:
                self._process_control_data(control_data)

            # clean all report data
            # self.__clean_node_check_list()

    def change_node_confirmation_target(self, node_name):
        if self.node_check_name is None:
            self.node_check_name = node_name
            print "confirmation target node:", self.node_check_name
        else:
            return

    def __clean_node_check_list(self):
        node_length = len(self.node_check_list_buffer)
        # init all to be -1
        self.node_check_list_buffer = [-1] * node_length

    def get_status_report(self, node_name, report_data):
        try:
            node_index = self.all_nodes_name.index(node_name)
            self.node_check_list_buffer[node_index] = report_data

        except ValueError:
            print "can't find node: ", node_name

        # try:
        #     if report_data is True:
        #         self.update_node_and_link(node_name, command)
        #
        #         # print self.all_topics_name
        #
        #         index = self.all_nodes_name.index(node_name)
        #         self.node_check_list[index] = report_data
        #
        # except ValueError:
        #     print('no this node')
        #     return

    # virtual function
    def _process_control_data(self, status):
        pass

    # virtual method
    def update_node_and_link(self, node, commands):
        pass

    # udpate app output locks
    def update_apps_reource_block_list(self):
        # get length and init block_list with resource_list length
        length_list = len(self.apps_resource_list)
        app_resource_block_list = [[]] * (length_list)

        # reverse app resource list
        for i in range(length_list-1, -1, -1):
            types = self.apps_resource_list[i]
            # protect empty list
            if len(types) == 0:
                continue
            # loop all the types in this app
            for msg_type in types:
                # loop the rest list
                # print "block list: ", app_resource_block_list
                for j in range(i-1, -1, -1):

                    # try to find the given type and append it the block list
                    try:
                        self.apps_resource_list[j].index(msg_type)
                        # block, use another segment of storage by importing copy module
                        block = copy.copy(app_resource_block_list[j])
                        if block.count(msg_type) == 0:
                            block.append(msg_type)
                            app_resource_block_list[j] = block

                    # failed to find type in this app, continue
                    except ValueError:
                        continue

        self.apps_resource_block_list = app_resource_block_list

    def update_all_apps_lock(self):

        length_apps = len(self.all_app_node_names)
        # loop over all active apps
        for i in range(length_apps):
            # get node object by name
            app_name = self.all_app_node_names[i]
            index = self.all_nodes_name.index(app_name)
            app_node_object = self.all_nodes[index]
            # update node block
            app_node_object.update_out_message_type_lock(self.apps_resource_block_list[i])


if __name__ == '__main__':
    master = Master()

    master.apps_resource_list = [["arm_command", "wheel_command", "cloud_deck_command", "voice_command"], ["cloud_deck_command", "voice_command"]]
    master.update_apps_reource_block_list()
    print master.apps_resource_block_list





