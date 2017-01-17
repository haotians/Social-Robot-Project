# coding=utf-8
import serial
<<<<<<< HEAD
import library.motion_control.WheelNode
import library.motion_control.SerialTransmit
import Components
import library.motion_control.ArmNode
import DecisionTree as DT
import library.voice.Voice as voice
import library.gui.UIControl as UI
import library.vision.Vision.Vision as vision
import application.TrainFaceRecognition as tfr
import application.DefaultControl as defaultcontrol


class WholeSystem(Components.Master):
=======
import library.gpu_accelerate.pyopencl_convolution as gpu


class WholeSystem(Master.Master):
>>>>>>> 855f04aa101166a35a8f64b73927ce340cd4ca1b
    def __init__(self):
        Components.Master.__init__(self)

    def create_a_node(self, node_type):
        # type list:
        #
        # sensor_listener
        # serial_transmit
        # wheel_node
        # arm_node
        # voice_node
        # dt_node
        # UI_node
        # app_train_face
        # vision_node

        a_object = None
        if node_type is 'sensor_listener':
            a_object = library.motion_control.SensorListener.SensorListener(self)
        elif node_type is 'serial_transmit':
            a_object = library.motion_control.SerialTransmit.SerialTransmit(self)
        elif node_type is 'wheel_node':
            a_object = library.motion_control.WheelNode.WheelNode(self)
        elif node_type is 'arm_node':
            a_object = library.motion_control.ArmNode.ArmNode(self)
        elif node_type is 'voice_sys':
            a_object = voice.Voice(self)
        elif node_type is 'dt_sys':
            a_object = DT.DecisionTree(self)
            self.dt_node = a_object
        elif node_type is 'UI_sys':
            a_object = UI.RobotControl(self)
        elif node_type is 'app_train_face':
            a_object = tfr.TrainFaceRecognition(self)
        elif node_type is 'vision_sys':
            a_object = vision.Vision(self)
        elif node_type is 'default_control':
            a_object = defaultcontrol.DefaultControl(self)
        return a_object

    def initial_system(self):

        # We start the system with several essential nodes
        # here, I start with a serial transmit and a topic which send information to this node
        # ser_wheel = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=None)
        # self.add_node('serial_transmit', 'wheel_serial', [ser_wheel, 8, 14, "wheel_imu_sonar"])
        # self.add_topic('wheel_control_to_wheel_serial')
        # self.link_node_topic('wheel_serial', 'wheel_control_to_wheel_serial', 'input_of_node')
        #
        # # then, I test SensorListener node.
        # self.add_node('sensor_listener', 'sensor_listener')
        # self.add_topic('wheel_serial_to_sensor_listener')
        # self.add_topic('sensor_listener_to_someone')
        # self.link_node_topic('wheel_serial', 'wheel_serial_to_sensor_listener', 'output_of_node')
        # self.link_node_topic('sensor_listener', 'wheel_serial_to_sensor_listener', 'input_of_node')
        # self.link_node_topic('sensor_listener', 'sensor_listener_to_someone', 'output_of_node')
        #
        # # then, test WheelNode node
        # self.add_node('wheel_node', 'wheel_control')
        # self.add_topic('decision_tree_to_wheel_control')
        # self.link_node_topic('wheel_control', 'wheel_control_to_wheel_serial', 'output_of_node')
        # self.link_node_topic('wheel_control', 'decision_tree_to_wheel_control', 'input_of_node')

        # self.add_topic('sensor_listener_to_UI_control')
        # self.link_node_topic('wheel_serial', 'wheel_serial_to_sensor_listener', 'output_of_node')
        # self.link_node_topic('sensor_listener', 'wheel_serial_to_sensor_listener', 'input_of_node')
        # self.link_node_topic('sensor_listener', 'sensor_listener_to_UI_control', 'output_of_node')
        #
        # # then, test WheelNode node
        # self.add_node('wheel_node', 'wheel_control')
        # self.link_node_topic('wheel_control', 'wheel_control_to_wheel_serial', 'output_of_node')
        #
        # # then, add UI
        # self.add_node('UI_node', 'UI_control')
        # self.add_topic('UI_control_to_wheel_control')
        # self.link_node_topic('UI_control', 'UI_control_to_wheel_control', 'output_of_node')
        # self.link_node_topic('wheel_control', 'UI_control_to_wheel_control', 'input_of_node')
        # self.link_node_topic('UI_control', 'sensor_listener_to_UI_control', 'input_of_node')

        # initialize decision tree
        self.add_node('dt_sys', 'dt_node')

        # initialize voice system
        self.add_node('voice_sys', 'voice_node')
        self.init_topic_and_link('dt_node', 'voice_node', 'topic_voice2dt', 'bothway', 'topic_dt2voice')

        # initialize UI system
        self.add_node('UI_sys', 'UI_node')
        self.init_topic_and_link('dt_node', 'UI_node', 'topic_UI2dt', 'bothway', 'topic_dt2UI')

        # initialize vision system
        self.add_node('vision_sys','vision_node')
        self.init_topic_and_link('dt_node', 'vision_node', 'topic_vision2dt', 'bothway', 'topic_dt2vision')

        self.add_node('wheel_node', 'wheel_control')
        self.init_topic_and_link('dt_node', 'wheel_control', 'topic_wheel2dt', 'bothway', 'topic_dt2wheel')

    def test_arm(self):
        ser_arm = serial.Serial("/dev/ttyACM1", baudrate=115200, timeout=None)
        self.add_node('serial_transmit', 'arm_serial', [ser_arm, 21, 20, "arm_head"])
        self.add_topic('arm_control_to_arm_serial')
        self.link_node_topic('arm_serial', 'arm_control_to_arm_serial', 'input_of_node')

        self.add_node('arm_node', 'arm_control')
        self.add_topic('decision_tree_to_arm_control')
        self.link_node_topic('arm_control', 'arm_control_to_arm_serial', 'output_of_node')
        self.link_node_topic('arm_control', 'decision_tree_to_arm_control', 'input_of_node')

    def test_wheel_ui(self):
        self.add_node('wheel_node', 'wheel_control')
        self.add_node('UI_sys', 'UI_control')
        self.add_topic('UI_control_to_wheel_control')
        self.link_node_topic('UI_control', 'UI_control_to_wheel_control', 'output_of_node')
        self.link_node_topic('wheel_control', 'UI_control_to_wheel_control', 'input_of_node')

        ser_wheel = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=None)
        self.add_node('serial_transmit', 'wheel_serial', [ser_wheel, 8, 14, "wheel_imu_sonar"])
        self.add_topic('wheel_control_to_wheel_serial')
        self.link_node_topic('wheel_serial', 'wheel_control_to_wheel_serial', 'input_of_node')
        self.link_node_topic('wheel_control', 'wheel_control_to_wheel_serial', 'output_of_node')

        self.add_node('sensor_listener', 'sensor_listener')
        self.add_topic('wheel_serial_to_sensor_listener')
        self.link_node_topic('wheel_serial', 'wheel_serial_to_sensor_listener', 'output_of_node')
        self.link_node_topic('sensor_listener', 'wheel_serial_to_sensor_listener', 'input_of_node')

    def test_wheel_arm_ui(self):
        self.add_node('wheel_node', 'wheel_control')
        self.add_node('UI_sys', 'UI_control')
        self.add_topic('UI_control_to_wheel_control')
        self.link_node_topic('UI_control', 'UI_control_to_wheel_control', 'output_of_node')
        self.link_node_topic('wheel_control', 'UI_control_to_wheel_control', 'input_of_node')

        ser_wheel = serial.Serial("/dev/ttyACM1", baudrate=115200, timeout=None)
        self.add_node('serial_transmit', 'wheel_serial', [ser_wheel, 8, 14, "wheel_imu_sonar"])
        self.add_topic('wheel_control_to_wheel_serial')
        self.link_node_topic('wheel_serial', 'wheel_control_to_wheel_serial', 'input_of_node')
        self.link_node_topic('wheel_control', 'wheel_control_to_wheel_serial', 'output_of_node')

        self.add_node('sensor_listener', 'sensor_listener')
        self.add_topic('wheel_serial_to_sensor_listener')
        self.link_node_topic('wheel_serial', 'wheel_serial_to_sensor_listener', 'output_of_node')
        self.link_node_topic('sensor_listener', 'wheel_serial_to_sensor_listener', 'input_of_node')

<<<<<<< HEAD:ewaybot_vision/WholeSystem.py
        ser_arm = serial.Serial("/dev/ttyACM0", baudrate=115200, timeout=None)
        self.add_node('serial_transmit', 'arm_serial', [ser_arm, 19, 16, "arm_head"])
=======
        ser_arm = serial.Serial("/dev/ttyACM1", baudrate=115200, timeout=None)
        self.add_node('serial_transmit', 'arm_serial', [ser_arm, 21, 20, "arm_head"])
>>>>>>> b938384293338862077a53f78dbaa155f21acf2b:legacy/WholeSystem.py
        self.add_topic('arm_control_to_arm_serial')
        self.link_node_topic('arm_serial', 'arm_control_to_arm_serial', 'input_of_node')

        self.add_node('arm_node', 'arm_control')
        self.add_topic('UI_control_to_arm_control')
        self.link_node_topic('arm_control', 'arm_control_to_arm_serial', 'output_of_node')
        self.link_node_topic('arm_control', 'UI_control_to_arm_control', 'input_of_node')
        self.link_node_topic('UI_control', 'UI_control_to_arm_control', 'output_of_node')

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


if __name__ == '__main__':

<<<<<<< HEAD:ewaybot_vision/WholeSystem.py
    robot_sys = WholeSystem()
    # robot_sys.initial_system()
    # robot_sys.test_wheel_ui()
    # robot_sys.test_wheel_arm_ui()
    robot_sys.check_node_status()
=======
    # robot_sys = WholeSystem()
    # robot_sys.initial_system()
    # # robot_sys.test_wheel_ui()
    # # robot_sys.test_wheel_arm_ui()
    # robot_sys.check_node_status()
    gpu.gpu_convolution([[3, 1, 1, 4, 8, 2, 1, 3],
                         [4, 2, 1, 1, 2, 1, 2, 3],
                         [4, 4, 4, 4, 3, 2, 2, 2],
                         [9, 8, 3, 8, 9, 0, 0, 0],
                         [9, 3, 3, 9, 0, 0, 0, 0],
                         [0, 9, 0, 8, 0, 0, 0, 0],
                         [3, 0, 8, 8, 9, 4, 4, 4],
                         [5, 9, 8, 1, 8, 1, 1, 1]],
                        [[1, 1, 1],
                         [1, 0, 1],
                         [1, 1, 1]])
>>>>>>> b938384293338862077a53f78dbaa155f21acf2b:legacy/WholeSystem.py
    # robot_sys.test_arm()
    # robot_sys.start_thread()


