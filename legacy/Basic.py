class BasicCommand(object):

    def __init__(self):

        # wheel data
        # format:   0 null null null null                           do nothing
        #           1 angle speed null null                         UI control
        #           2 mode dis/angle speed radius                   voice/Vision control
        #             mode = 1 : wheel forward  (radius is not support in this mode)
        #             mode = 2 : wheel backward (radius is not support in this mode)
        #             mode = 3 : wheel leftward
        #             mode = 4 : wheel rightward
        self.data_wheels = [0, 0, 0, 0, 0]
        # arm data
        # format:   0 null null null null null null                 do nothing
        #           1 left(x y z) right(x,y,z)                      cartesian move
        #           2 type file_name null null null null            build_in_move
        #             type = 1 : arm init_shutdown
        #             type = 2 : arm init_work
        #             type = 3 : arm movement according to file_name (non-music)
        #             type = 4 : arm movement according to file_name (music)
        #             type = 5 : arm start record trajectory into file_name
        #             type = 6 : arm end record trajectory
        self.data_arms = [0, 0, 0, 0, 0, 0, 0]
        # cloud deck data
        # format:   0 null null null null null null                 do nothing
        #           1 angle1 speed1 angle2 speed2 angle3 speed3     direct control
        #           2 type null null null null null                 build_in_move
        self.data_cloud_deck = [0, 0, 0, 0, 0, 0, 0]
        # flag
        self.data_flag = False

        # control Data
        # 0 NULL

        # 1 camera off
        # 2 camera on local only
        # 3 camera on web only
        # 4 camera on local and web
        # 5 training new person for local face

        # 11 voice off
        # 12 voice on web
        # 13 voice on local
        self.data_control = 0

    def output_command(self):
        return self.data_flag, self.data_wheels, self.data_arms, self.data_cloud_deck, self.data_control

    def clean_command_arms(self):
        self.data_arms = [0, 0, 0, 0, 0, 0, 0]
        self.clean_command_flag()

    def clean_command_wheels(self):
        self.data_wheels = [0, 0, 0, 0, 0]
        self.clean_command_flag()

    def clean_command_cloud_deck(self):
        self.data_cloud_deck = [0, 0, 0, 0, 0, 0, 0]
        self.clean_command_flag()

    def clean_data_control(self):
        self.data_control = 0
        self.clean_command_flag()

    def clean_command_flag(self):
        self.data_flag = False

    # camera operation
    def camera_off(self):
        self.data_control = 1
        self.data_flag = True

    def camera_on_ui(self):
        self.data_control = 3
        self.data_flag = True

    def camera_on_local(self):
        self.data_control = 2
        self.data_flag = True

    def camera_on_ui_local(self):
        self.data_control = 4
        self.data_flag = True

    # voice operation
    def voice_on_web(self):
        self.data_control = 12
        self.data_flag = True

    def voice_on_local(self):
        self.data_control = 13
        self.data_flag = True

    def voice_off(self):
        self.data_control = 11
        self.data_flag = True

    # wheel operation
    def wheel_forward(self, dis=None, speed=None, radius=None):
        if dis is None:
            dis = 0
        if speed is None:
            speed = 0
        self.data_wheels = [1, 1, dis, speed, 0]
        self.data_flag = True

    def wheel_backward(self, dis=None, speed=None, radius=None):
        if dis is None:
            dis = 0
        if speed is None:
            speed = 0
        self.data_wheels = [1, 2, dis, speed, 0]
        self.data_flag = True

    def wheel_turnleft(self, angle=None, speed=None, radius=None):
        if angle is None:
            angle = 0
        if speed is None:
            speed = 0
        if radius is None:
            radius = 0
        self.data_wheels = [1, 3, angle, speed, radius]
        self.data_flag = True

    def wheel_turnright(self, angle=None, speed=None, radius=None):
        if angle is None:
            angle = 0
        if speed is None:
            speed = 0
        if radius is None:
            radius = 0
        self.data_wheels = [1, 4, angle, speed, radius]
        self.data_flag = True

    def wheel_stop(self):
        self.data_wheels = [0, 0, 0, 0, 0]
        self.data_flag = True

    # arm related method
    def arm_init_shutdown(self):
        self.data_arms = [1, 1, 0, 0, 0, 0, 0]
        self.data_flag = True

    def arm_init_work(self):
        self.data_arms = [1, 2, 0, 0, 0, 0, 0]
        self.data_flag = True

    def arm_move_non_music(self, file_name=None):
        self.data_arms = [1, 3, file_name, 0, 0, 0, 0]
        self.data_flag = True

    def arm_move_music(self, file_name=None):
        self.data_arms = [1, 4, file_name, 0, 0, 0, 0]
        self.data_flag = True

    def arm_record_trajectory(self):
        self.data_arms = [1, 5, 0, 0, 0, 0, 0]
        self.data_flag = True

    def arm_end_record_trajectory(self):
        self.data_arms = [1, 6, 0, 0, 0, 0, 0]
        self.data_flag = True

    # cloud deck operation
    def cloud_deck_direct_control(self, angle1=None, speed1=None, angle2=None, speed2=None, angle3=None, speed3=None):
        if angle1 is None:
            angle1 = 0
        if speed1 is None:
            speed1 = 0
        if angle2 is None:
            angle2 = 0
        if speed2 is None:
            speed2 = 0
        if angle3 is None:
            angle3 = 0
        if speed3 is None:
            speed3 = 0
        self.data_cloud_deck = [0, angle1, speed1, angle2, speed2, angle3, speed3]

    def cloud_deck_build_in_move(self, type=None):
        if type is None:
            type = 0
        self.data_cloud_deck = [1, type, 0, 0, 0, 0, 0]
        self.data_flag = True
