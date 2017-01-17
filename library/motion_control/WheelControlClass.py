

class WheelControlClass(object):
    # This class defined several common motion for robot arm control.
    # Created Data: 2015-11-19 Version 2015-11-19
    def __init__(self):
        # control cycle is 50 ms
        self.control_cycle = 50

    def ui_to_wheel(self, speed, angle):

        # transform speed from 0 - 100 to 0 - 1 m/s
        speed *= 0.005
        # set the limit, 200 is the maximum speed
        if speed > 0.5:
            speed = 0.5

        # map the angle to wheel control direction
        # the whole panel is separated into four parts
        direction = [0, 0]
        if 90 > angle >= 0:
            direction[0] = 1.0 - 0.5 / 90 * angle
            direction[1] = 1.0 - 1.5 / 90 * angle
        elif 180 > angle >= 90:
            direction[0] = 0.5 - 1.5 / 90 * (angle - 90)
            direction[1] = -0.5 - 0.5 / 90 * (angle - 90)
        elif 270 > angle >= 180:
            direction[0] = -1.0 + 0.5 / 90 * (angle - 180)
            direction[1] = -1.0 + 1.5 / 90 * (angle - 180)
        else:
            direction[0] = -0.5 + 1.5 / 90 * (angle - 270)
            direction[1] = 0.5 + 0.5 / 90 * (angle - 270)

        # map the control direction to rotate_direction
        # since the serial port can only transfer positive number,
        # we map 0 - 250 to 0 - 250 and 0 - (-250) to 250 - 500
        wheel_speed = [0, 0]
        wheel_acceleration = [0, 0]
        for i in range(2):
            # the positive is forward direction
            wheel_speed[i] = direction[i] * speed
            wheel_acceleration[i] = direction[i]

        output = self.move_a_distance([5, 5], wheel_speed, [0, 0], wheel_acceleration)
        return output

    def straight(self, distance, speed):
        if distance * speed < 0:
            speed = -speed
        output = self.move_a_distance([distance, distance], [speed, speed], [0, 0], [0.3, 0.3])
        return output

    def circle(self, angle, radius, speed):
        # at here, speed is a positive number. the direction is given by the combination of angle and radius
        speed = speed
        acceleration = 0.3
        # the distance between the center and the wheel is 0.165m
        l = 0.1648
        wheel_distance = [0, 0]
        wheel_speed = [0, 0]
        wheel_acceleration = [0, 0]
        sign = [-1, 1]

        temp_ratio = [0, 0]
        if radius == 0:
            temp_ratio = [-1, 1]
        else:
            for i in range(2):
                temp_ratio[i] = (radius + sign[i] * l) / radius

        for i in range(2):
            wheel_distance[i] = (radius + sign[i] * l) * angle
            wheel_speed[i] = speed * temp_ratio[i] / max([abs(temp_ratio[0]), abs(temp_ratio[1])])
            wheel_acceleration[i] = abs(acceleration * temp_ratio[i] / max([abs(temp_ratio[0]), abs(temp_ratio[1])]))
            if wheel_speed[i] * wheel_distance[i] < 0:
                wheel_speed[i] = -wheel_speed[i]

        output = self.move_a_distance(wheel_distance, wheel_speed, [0, 0], wheel_acceleration)
        return output

    def move_a_distance(self, distance, speed, end_speed=[0, 0], acceleration=[0.1, 0.1]):
        # the unit of distance, speed and acceleration are m, m/s, and m/s^2
        # this method is for both wheels. So distance, speed and acceleration are lists

        # the actual distance travelled is not exact equal to the given distance, need to improve accuracy
        current_speed = [0, 0]
        # current_speed = self.get_current_speed() # need to write a new method
        switch_point = [0, 0]
        for i in range(2):
            # change format and set limit
            distance[i] = float(min(distance[i], 10))
            distance[i] = float(max(distance[i], -10))

            speed[i] = float(min(speed[i], 1))
            speed[i] = float(max(speed[i], -1))

            end_speed[i] = float(min(end_speed[i], 1))
            end_speed[i] = float(max(end_speed[i], -1))

            acceleration[i] = float(min(acceleration[i], 1))
            acceleration[i] = float(max(acceleration[i], -1))

            # calculate switch_point
            switch_point[i] = self.calculate_switch_point(distance[i], current_speed[i],
                                                          speed[i], end_speed[i], acceleration[i])
        output = self.transmit_to_output(switch_point, speed, end_speed, acceleration)
        return output

    def calculate_switch_point(self, distance, current_speed, goal_speed, end_speed=0, acceleration=0.1):
        # this method calculate switch point for one wheel. units are in terms of impulse.
        # the first switch point is when the wheel stop speeding up, the second is when the wheel start deceleration.

        distance = float(distance)
        current_speed = float(current_speed)
        goal_speed = float(goal_speed)
        end_speed = float(end_speed)
        acceleration = float(acceleration)
        # first, check whether the wheel have enough time to speed up to goal speed
        acc_distance1 = self.calculate_distance_with_constant_acceleration(current_speed, goal_speed, acceleration)
        acc_distance2 = self.calculate_distance_with_constant_acceleration(goal_speed, end_speed, acceleration)
        acc_distance = acc_distance1 + acc_distance2
        # then, find switch point
        if abs(distance) > abs(acc_distance):
            switch_point = distance - acc_distance2
        else:
            switch_point = (-acc_distance2 + acc_distance1 + distance) / 2
        return switch_point

    def calculate_distance_with_constant_acceleration(self, start_speed, end_speed, acceleration):
        start_speed = float(start_speed)
        end_speed = float(end_speed)
        acceleration = float(abs(acceleration))

        if acceleration == 0:
            distance = 0
        else:
            distance = (end_speed + start_speed) * abs(end_speed - start_speed) / (2 * acceleration)
        return distance

    def transmit_to_output(self, switch_point, goal_speed, end_speed, acceleration):
        # this method change units from m, m/s, m/s^2 to switch_times, switch_frequency, switch_frequency/s
        # for one round, 1200 switch times. So 1 round/s = 1200 Hz. 1 round/s^2 = 1200 Hz/s
        switch_per_round = 1200

        # the diameter of the wheel is 0.152 m, so the perimeter is pi * 0.152 = 0.477 m
        perimeter = 0.495

        # switch point should always be positive, speeds can be both positive and negative.
        # the moving direction is determined by speeds.
        # acceleration should always be positive
        switch_point_output = [0, 0]
        goal_speed_output = [0, 0]
        end_speed_output = [0, 0]
        acceleration_output = [0, 0]
        for i in range(2):
            switch_point_output[i] = int(abs(switch_point[i]) / perimeter * switch_per_round)
            goal_speed_output[i] = int(goal_speed[i] / perimeter * switch_per_round * 10)
            if goal_speed_output[i] < 0:
                goal_speed_output[i] += 65536
            end_speed_output[i] = int(end_speed[i] / perimeter * switch_per_round * 10)
            if end_speed_output[i] < 0:
                end_speed_output[i] += 65536
            acceleration_output[i] = int(abs(acceleration[i]) / perimeter * switch_per_round * 10)

        output = [0, switch_point_output[0], goal_speed_output[0], end_speed_output[0], acceleration_output[0],
                  switch_point_output[1], goal_speed_output[1], end_speed_output[1], acceleration_output[1]]
        # print(output)
        return output
