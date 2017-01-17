# coding=utf-8
import time
import copy

import components.Components


class SerialTransmit(components.Components.Node):
    def __init__(self, master_object, ser=None, send_num=0, receive_num=0):
        components.Components.Node.__init__(self, master_object)
        self.name = 'SerialTransmit'
        self.ser = ser
        self.send_num = send_num
        self.receive_num = receive_num
        self.current_state = []  # data of current servo state
        self.output_type = "wheel_imu_sonar"

    def set_node_status(self, init_parameter):
        self.set_serial_port(init_parameter[0])
        self.set_data_length(init_parameter[1], init_parameter[2])
        self.output_type = init_parameter[3]

    def set_serial_port(self, ser):
        self.ser = ser

    def set_data_length(self, send_num, receive_num):
        self.send_num = send_num
        self.receive_num = receive_num

    def _node_run(self):
        print 'serial sys has been started'
        time.sleep(1)
        signal = 'f'  # a flag used to determine whether putting data into serial port
        commands_to_serial = []

        while self.thread_active:
            # print "serial transmit stage 1"
            # Part 1: read all message:
            messages = self.get_messages_from_all_topics()
            # if len(messages)>0:
            #     print "serialmsgreceived"
            # Part 2: use these messages to generate commands for each topic

            # Part 2.1: we just want only one message which has proper format
            num_active_source = 0
            for i in range(len(messages)):
                if messages[i] is not None:
                    # print "serial msg: ", messages[i]
                    num_active_source += 1
                    msg_time, msg_type, data, source = self.message_object.message_dewarp(messages[i])
            if num_active_source == 1 and (msg_type == 81 or msg_type == 82):
                commands_to_serial = copy.deepcopy(data)
            # the commands_to_serial is in the form of :[ [..., ..., ...], [..., ..., ...], ... ]

            # Part 2.2: send command through serial port
            if signal == 'n':  # check the signal flag to decide whether or not to send command
                signal = 'f'  # set the flag to be false
                if not commands_to_serial == []:  # check whether the queue is empty
                    # transfer data into proper form. For 16 bits data, 2 characters are needed. For 8bit, 1 chr is good
                    current_command = commands_to_serial.pop(0)
                    # print self.name, current_command
                    # first, transmit a 0xff as a head
                    self.ser.write(chr(int(0xff)))
                    aaa = current_command.pop(0)
                    self.ser.write(chr(int(aaa)))
                    for i in range(self.send_num):
                        # each data is 16 bits
                        aaa = current_command.pop(0)
                        temp_aaa = chr(int(aaa & 0xff))
                        self.ser.write(temp_aaa)
                        temp_aaa = chr(int((aaa >> 8) & 0xff))
                        self.ser.write(temp_aaa)
                    # at end, transmit a 0xee as a tail
                    self.ser.write(chr(int(0xee)))
            time.sleep(0.0002)

            # Part 2.3 & Part 3: read status from serial port and send status to topics
            while self.ser.inWaiting() >= 2 + 2 * self.receive_num:
                time1 = time.time()
                # read serial port
                signal = self.ser.read()
                if signal == 'n' or signal == 'm':
                    temp_current_state = []
                    temp_flag = self.ser.read()
                    temp_current_state.append(int(ord(temp_flag)))
                    for i in range(self.receive_num):
                        # read the first data, 16 bit
                        temp_low = self.ser.read()
                        temp_high = self.ser.read()
                        temp_whole = 256 * ord(temp_high) + ord(temp_low)
                        temp_current_state.append(int(temp_whole))

                    self.current_state = temp_current_state

                # if self.ser.inWaiting() > 2*(2 + 2 * self.receive_num):
                #     self.ser.flushInput()
                # print time.time()
                # print 'input from arduino', self.current_state

                if self.current_state != []:
                    commands = [self.message_object.message_warp(self.output_type, self.current_state)]
                    # Part 3: output commands
                    self.output_all_messages(commands)
            # print "serial transmit stage 4"
            # Part 4: report to master
            self.output_status_to_master(False)
            # this sleep time can not be too large, due to the control cycle limit of arduino
            time.sleep(0.0002)
