from scipy import constants


class HeadControlClass(object):
    # This class defined several common motion for robot arm control.
    # Created Data: 2015-12-27 Version 2015-12-27
    def __init__(self):
        # control cycle is 20 ms
        self.control_cycle = 20
        self.current_servo = [2048, 30, 2048, 30, 0]

    def create_control_data(self, data):
        command = self.a_simple_method(data)

        trajectory = list()
        trajectory.append(command)
        return trajectory

    def a_simple_method(self, data):
        if self.current_servo[4] == 0 and (data[1] != 0 or data[2] != 0):return self.current_servo

        # set limits
        if data[1] > 179:
            data[1] = 179
        elif data[1] < -179:
            data[1] = -179
        # from angle to 0 - 2048
        servo_9 = 2048 + data[1] * 2048 / 180

        if data[2] > 10:
            data[2] = 10
        elif data[2] < -10:
            data[2] = -10
        # from angle to 0 - 2048
        servo_10 = 2048 + data[2] * 2048 / 180

        if data[0] == 0:
            # move down, when moving down, servo should be at original position
            self.current_servo[4] = 0
            self.current_servo[0] = 2048
            self.current_servo[2] = 2048
        elif data[0] == 1:
            # move up
            self.current_servo[4] = 1
            self.current_servo[0] = servo_9
            self.current_servo[2] = servo_10
        elif data[0] == 2:
            # do nothing
            pass
        return self.current_servo
