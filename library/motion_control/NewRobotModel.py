import numpy as np
from scipy import constants
from scipy import optimize

import OneLink


class RobotModel(object):

    def __init__(self):
        self.parameters = [0.48, 0.15, 0.06, 0.05, 0.20, 0.335]

        self.links = []

        self.links.append(OneLink.OneLink())
        self.links[0].index = 0
        self.links[0].name = 'base'
        self.links[0].angle = 0.0
        self.links[0].axis = np.array([0, 0, 1])
        self.links[0].offset = np.array([0.0, 0.0, 0.0])
        self.links[0].position = np.array([0.0, 0.0, 0.0])
        self.links[0].angle_limits = np.array([0, 0])
        self.links[0].orientation = np.eye(3)

        # link1 - link3 are left shoulder using y-z-y layout
        self.links.append(OneLink.OneLink())
        self.links[1].index = 1
        self.links[1].name = 'left_shoulder_1'
        self.links[1].parent = 0
        self.links[1].angle = 0.0
        self.links[1].axis = np.array([0, 1, 0])
        self.links[1].offset = np.array([0.0, self.parameters[1], self.parameters[0]])
        self.links[1].position = np.array([0.0, 0.0, 0.0])
        self.links[1].angle_limits = np.array([-0.5 * constants.pi, 0.2 * constants.pi])
        self.links[1].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[2].index = 2
        self.links[2].name = 'left_shoulder_2'
        self.links[2].parent = 1
        self.links[2].angle = 0.0
        self.links[2].axis = np.array([0, 0, 1])
        self.links[2].offset = np.array([0.0, self.parameters[2], 0.0])
        self.links[2].position = np.array([0.0, 0.0, 0.0])
        self.links[2].angle_limits = np.array([-0.3 * constants.pi, 0.3 * constants.pi])
        self.links[2].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[3].index = 3
        self.links[3].name = 'left_shoulder_3'
        self.links[3].parent = 2
        self.links[3].angle = 0.0
        self.links[3].axis = np.array([0, 1, 0])
        self.links[3].offset = np.array([0.0, self.parameters[3], 0.0])
        self.links[3].position = np.array([0.0, 0.0, 0.0])
        self.links[3].angle_limits = np.array([-0.1 * constants.pi, 0.5 * constants.pi])
        self.links[3].orientation = np.eye(3)

        # robot(4) is the left elbow
        self.links.append(OneLink.OneLink())
        self.links[4].index = 4
        self.links[4].name = 'left_elbow'
        self.links[4].parent = 3
        self.links[4].angle = 0.0
        self.links[4].axis = np.array([1, 0, 0])
        self.links[4].offset = np.array([0.0, self.parameters[4], 0.0])
        self.links[4].position = np.array([0.0, 0.0, 0.0])
        self.links[4].angle_limits = np.array([0 * constants.pi, 0.5 * constants.pi])
        self.links[4].orientation = np.eye(3)

        # link6 - link8 are right shoulder using y-z-y layout
        self.links.append(OneLink.OneLink())
        self.links[5].index = 5
        self.links[5].name = 'right_shoulder_1'
        self.links[5].parent = 0
        self.links[5].angle = 0.0
        self.links[5].axis = np.array([0, 1, 0])
        self.links[5].offset = np.array([0.0, -self.parameters[1], self.parameters[0]])
        self.links[5].position = np.array([0.0, 0.0, 0.0])
        self.links[5].angle_limits = np.array([-0.5 * constants.pi, 0.2 * constants.pi])
        self.links[5].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[6].index = 6
        self.links[6].name = 'right_shoulder_2'
        self.links[6].parent = 5
        self.links[6].angle = 0.0
        self.links[6].axis = np.array([0, 0, 1])
        self.links[6].offset = np.array([0.0, -self.parameters[2], 0.0])
        self.links[6].position = np.array([0.0, 0.0, 0.0])
        self.links[6].angle_limits = np.array([-0.3 * constants.pi, 0.3 * constants.pi])
        self.links[6].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[7].index = 7
        self.links[7].name = 'right_shoulder_3'
        self.links[7].parent = 6
        self.links[7].angle = 0.0
        self.links[7].axis = np.array([0, 1, 0])
        self.links[7].offset = np.array([0.0, -self.parameters[3], 0.0])
        self.links[7].position = np.array([0.0, 0.0, 0.0])
        self.links[7].angle_limits = np.array([-0.1 * constants.pi, 0.5 * constants.pi])
        self.links[7].orientation = np.eye(3)

        # robot(9) is the right elbow
        self.links.append(OneLink.OneLink())
        self.links[8].index = 8
        self.links[8].name = 'right_elbow'
        self.links[8].parent = 7
        self.links[8].angle = 0.0
        self.links[8].axis = np.array([1, 0, 0])
        self.links[8].offset = np.array([0.0, -self.parameters[4], 0.0])
        self.links[8].position = np.array([0.0, 0.0, 0.0])
        self.links[8].angle_limits = np.array([-0.5 * constants.pi, 0 * constants.pi])
        self.links[8].orientation = np.eye(3)

    def set_angles(self, angles):
        for i in range(len(self.links)):
            self.links[i].angle = angles[i]

    def get_angles(self):
        angles = np.zeros(len(self.links))
        for i in range(len(self.links)):
            angles[i] = self.links[i].angle
        return angles

    def generate_axis_angle_rotation_matrix(self, axis, angle):
        # generate axis angle rotation matrix
        # it is a common formulation of axis-angle representation
        # :return: rotation matrix

        c = np.cos(angle)
        s = np.sin(angle)
        t = 1 - c

        axis_length = 0
        for i in range(3):
            axis_length = axis_length + axis[i] * axis[i]

        axis /= np.sqrt(axis_length)
        x = axis[0]
        y = axis[1]
        z = axis[2]

        result = np.array([[t*x*x + c,   t*x*y - z*s, t*x*z + y*s],
                           [t*x*y + z*s, t*y*y + c,   t*y*z - x*s],
                           [t*x*z - y*s, t*y*z + x*s, t*z*z + c]])
        return result

    def calculate_point_position(self, link_index, rel_position):
        # this function calculate the position of a point
        # link_index is the index of link where the point is, rel_position is expressed in body frame.
        rotation_matrix = self.links[link_index].orientation
        offset = self.links[link_index].position
        position = offset + rotation_matrix.dot(rel_position)
        return position

    def forward_kinematics(self):
        # this function calculate forward kinematics. It generates the position and angle of each link one by one
        # This is the standard way to do forward kinematic

        # the base have no parent
        self.links[0].rotation = self.generate_axis_angle_rotation_matrix(self.links[0].axis, self.links[0].angle)
        self.links[0].orietation = self.links[0].rotation
        self.links[0].position = self.links[0].offset
        # the position of each link is based on its parent
        for i in (range(len(self.links) - 1)):
            parent = self.links[i+1].parent
            self.links[i+1].rotation = self.generate_axis_angle_rotation_matrix(self.links[i+1].axis,
                                                                                self.links[i+1].angle)
            self.links[i+1].orientation = self.links[parent].orientation.dot(self.links[i+1].rotation)
            r_offset = self.links[parent].orientation.dot(self.links[i+1].offset)
            self.links[i+1].position = self.links[parent].position + r_offset

    def inverse_kinematics(self, target_l, target_r, initial_angles=None):
        # inverse kinematics. use simple 'sqp' method to find angles.
        # target_l: left hand position
        # target_r: right hand position

        if initial_angles is None:
            # the initial guess use current angles
            x0 = self.get_angles()
        else:
            x0 = initial_angles
        # set boundaries of optimization
        bounds_temp = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        for i in range(len(self.links)):
            bounds_temp[i] = (self.links[i].angle_limits[0], self.links[i].angle_limits[1])
        # use optimization to solve inverse kinematics. the cost function is 'objective_inverse_kinematics'
        res = optimize.minimize(self.objective_inverse_kinematics, x0[0:len(self.links)], args=(target_l, target_r),
                                bounds=bounds_temp, method='SLSQP', tol=1e-6, options={'disp': True})
        # update angles
        self.set_angles(res.x)
        # update positions
        self.forward_kinematics()
        return res

    def objective_inverse_kinematics(self, angles, target_l, target_r):
        # the cost/objective function for inverse kinematics.
        # the cost is the square of the difference between targets and hands
        # angles: current angles
        # target_l: target of left hand
        # target_r: target of right hand

        # set angles
        self.set_angles(angles)
        # use forward kinematics to find the position of hands
        self.forward_kinematics()
        # calculate hand position
        hand_l = self.calculate_point_position(4, [0, self.parameters[5], 0])
        hand_r = self.calculate_point_position(8, [0, -self.parameters[5], 0])
        # calculate the difference
        hand_diff_l = target_l - hand_l
        hand_diff_r = target_r - hand_r
        # the square of difference
        value1 = hand_diff_l.dot(hand_diff_l)
        value2 = hand_diff_r.dot(hand_diff_r)
        # return costs
        return value1 + value2

    def random_sample_ik(self, target, current_angles):
        current_angles = np.array(current_angles)
        current_angles = current_angles.astype(float)
        res_list = list()
        if target[1] >= 0:
            hand = 'left'
            delta = 1
        else:
            hand = 'right'
            delta = 5

        # first, use current angel as initial guess
        init_guess = current_angles[delta:(delta+4)]
        res = self.one_hand_inverse_kinematics(target, hand, init_guess)
        print(res.fun)
        if res.fun < 0.001:
            res_list.append(res)

        # then, generate random samples as initial guess
        for i in range(30):
            init_guess = np.random.rand(4)
            for j in range(4):
                init_guess[j] = self.links[j+delta].angle_limits[0] + \
                                init_guess[j] * (self.links[j+delta].angle_limits[1] -
                                                 self.links[j+delta].angle_limits[0])

            res = self.one_hand_inverse_kinematics(target, hand, init_guess)
            # print(res.fun)
            if res.fun < 0.01:
                res_list.append(res)

        # pick up the closest result
        if len(res_list) == 0:
            print("target point is not in workspace")
            current_angles = None
        else:
            min_diff = 100
            for a_res in res_list:
                diff = a_res.x - current_angles[delta:(delta+4)]
                diff_square = diff.dot(diff)
                if diff_square < min_diff:
                    min_diff = diff_square
                    final_res = a_res.x
            current_angles[delta:(delta+4)] = final_res
            print current_angles
        return current_angles

    def one_hand_inverse_kinematics(self, target, hand, initial_angles=None):
        if hand == 'left':
            delta = 1
        else:
            delta = 5

        # set initial angle
        if initial_angles is None:
            x_temp = self.get_angles()
            x0 = x_temp[delta:(delta+4)]
        else:
            x0 = initial_angles

        bounds_temp = [(0, 0), (0, 0), (0, 0), (0, 0)]
        # set boundary
        for i in range(4):
            bounds_temp[i] = (self.links[i+delta].angle_limits[0], self.links[i+delta].angle_limits[1])

        # use optimization to solve inverse kinematics. the cost function is 'objective_inverse_kinematics'
        res = optimize.minimize(self.objective_inverse_kinematics_one_hand, x0, args=(target, hand),
                                bounds=bounds_temp, method='SLSQP')

        return res

    def objective_inverse_kinematics_one_hand(self, angles, target, hand):
        if hand == 'left':
            # left_hand
            for i in range(4):
                self.links[i+1].angle = angles[i]
            self.forward_kinematics()
            hand_l = self.calculate_point_position(4, [0, self.parameters[5], 0])
            diff = target - hand_l
        else:
            # right hand
            for i in range(4):
                self.links[i+5].angle = angles[i]
            self.forward_kinematics()
            hand_r = self.calculate_point_position(8, [0, -self.parameters[5], 0])
            diff = target - hand_r

        value = diff.dot(diff)
        return value

    def jacobian_left(self, angles):
        # calculate left hand jacobian.
        # it is generated by matlab symbolic toolbox. don't try to read this method...
        angle1 = angles[0]
        angle2 = angles[1]
        angle3 = angles[2]
        angle4 = angles[3]
        angle5 = angles[4]

        shoulder_x = self.parameters[0]
        shoulder_y = self.parameters[1]
        shoulder1 = self.parameters[2]
        shoulder2 = self.parameters[3]
        upper_arm = self.parameters[4]
        lower_arm = self.parameters[5]

        t2 = np.cos(angle1)
        t3 = np.sin(angle3)
        t4 = np.cos(angle2)
        t5 = np.cos(angle3)
        t6 = np.sin(angle1)
        t7 = t2*t5
        t9 = t3*t4*t6
        t8 = t7-t9
        t10 = np.sin(angle2)
        t11 = np.cos(angle4)
        t12 = np.sin(angle5)
        t13 = np.cos(angle5)
        t14 = np.sin(angle4)
        t15 = t3*t6
        t17 = t2*t4*t5
        t16 = t15-t17
        t18 = t5*t6
        t19 = t2*t3*t4
        t20 = t18+t19
        t21 = t14*t16
        t22 = t21-t2*t10*t11
        t23 = shoulder2*t3*t10
        t24 = t3*t10*upper_arm
        t25 = lower_arm*t4*t11*t12
        t26 = lower_arm*t3*t10*t13
        t27 = t23+t24+t25+t26-lower_arm*t5*t10*t12*t14
        t28 = t2*t3
        t29 = t4*t5*t6
        t30 = t28+t29
        t31 = t14*t30
        t32 = t6*t10*t11
        t33 = t31+t32
        j_left = np.array([1.0, 0.0, 0.0,
                           0.0, 1.0, 0.0,
                           0.0, 0.0, 1.0,
                           -shoulder1*t2-shoulder2*t8-shoulder_x*t2-t8*upper_arm-lower_arm*(t8*t13+t12*t33), -shoulder1*t6-shoulder2*t20-shoulder_x*t6-t20*upper_arm-lower_arm*(t13*t20+t12*t22), 0.0,
                           t2*t27, t6*t27, -lower_arm*(t12*(t10*t11+t4*t5*t14)-t3*t4*t13)+shoulder2*t3*t4+t3*t4*upper_arm,
                           lower_arm*(t13*t16-t12*t14*t20)+shoulder2*t16+t16*upper_arm, -lower_arm*(t13*t30-t8*t12*t14)-shoulder2*t30-t30*upper_arm, t10*(shoulder2*t5+t5*upper_arm+lower_arm*t5*t13+lower_arm*t3*t12*t14),
                           -lower_arm*t12*(t11*t16+t2*t10*t14), lower_arm*t12*(t11*t30-t6*t10*t14), -lower_arm*t12*(t4*t14+t5*t10*t11),
                           lower_arm*(t12*t20-t13*t22), -lower_arm*(t8*t12-t13*t33), lower_arm*(t13*(t4*t11-t5*t10*t14)-t3*t10*t12),
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0,
                           0.0, 0.0, 0.0])
        j_left = j_left.reshape(12, 3)
        j_left = j_left.T
        j_left_arm = j_left[:, 4:8]
        return j_left_arm

    def jacobian_right(self, angles):
        # calculate right hand jacobian.
        # it is generated by matlab symbolic toolbox. don't try to read this method...
        angle1 = angles[0]
        angle7 = angles[5]
        angle8 = angles[6]
        angle9 = angles[7]
        angle10 = angles[8]

        shoulder_x = self.parameters[0]
        shoulder_y = self.parameters[1]
        shoulder1 = self.parameters[2]
        shoulder2 = self.parameters[3]
        upper_arm = self.parameters[4]
        lower_arm = self.parameters[5]

        t2 = np.cos(angle1)
        t3 = np.sin(angle8)
        t4 = np.cos(angle7)
        t5 = np.cos(angle8)
        t6 = np.sin(angle1)
        t7 = t2*t5
        t9 = t3*t4*t6
        t8 = t7-t9
        t10 = np.sin(angle7)
        t11 = np.cos(angle9)
        t12 = np.sin(angle10)
        t13 = np.cos(angle10)
        t14 = np.sin(angle9)
        t15 = t3*t6
        t17 = t2*t4*t5
        t16 = t15-t17
        t18 = t5*t6
        t19 = t2*t3*t4
        t20 = t18+t19
        t21 = t14*t16
        t22 = t21-t2*t10*t11
        t23 = shoulder2*t3*t10
        t24 = t3*t10*upper_arm
        t25 = lower_arm*t4*t11*t12
        t26 = lower_arm*t3*t10*t13
        t27 = t23+t24+t25+t26-lower_arm*t5*t10*t12*t14
        t28 = t2*t3
        t29 = t4*t5*t6
        t30 = t28+t29
        t31 = t14*t30
        t32 = t6*t10*t11
        t33 = t31+t32
        j_right = np.array([1.0, 0.0, 0.0,
                            0.0, 1.0, 0.0,
                            0.0, 0.0, 1.0,
                            shoulder1*t2+shoulder2*t8+shoulder_x*t2+t8*upper_arm+lower_arm*(t8*t13+t12*t33), shoulder1*t6+shoulder2*t20+shoulder_x*t6+t20*upper_arm+lower_arm*(t13*t20+t12*t22), 0.0,
                            0.0, 0.0, 0.0,
                            0.0, 0.0, 0.0,
                            0.0, 0.0, 0.0,
                            0.0, 0.0, 0.0,
                            -t2*t27, -t6*t27, lower_arm*(t12*(t10*t11+t4*t5*t14)-t3*t4*t13)-shoulder2*t3*t4-t3*t4*upper_arm,
                            -lower_arm*(t13*t16-t12*t14*t20)-shoulder2*t16-t16*upper_arm, lower_arm*(t13*t30-t8*t12*t14)+shoulder2*t30+t30*upper_arm, -t10*(shoulder2*t5+t5*upper_arm+lower_arm*t5*t13+lower_arm*t3*t12*t14),
                            lower_arm*t12*(t11*t16+t2*t10*t14), -lower_arm*t12*(t11*t30-t6*t10*t14), lower_arm*t12*(t4*t14+t5*t10*t11),
                            -lower_arm*(t12*t20-t13*t22), lower_arm*(t8*t12-t13*t33), -lower_arm*(t13*(t4*t11-t5*t10*t14)-t3*t10*t12)])

        j_right = j_right.reshape(12, 3)
        j_right = j_right.T
        j_right_arm = j_right[:, 8:12]
        return j_right_arm

    def random_sample_point_direction(self, target, current_angles):
        current_angles = np.array(current_angles)
        current_angles = current_angles.astype(float)
        target = np.array(target)
        target = target.astype(float)

        res_list = list()
        # left_or_right = np.random.rand(1)
        left_or_right = [1]
        if left_or_right[0] >= 0.5:
            hand = 'left'
            delta = 1
            target = target - np.array([0.0, self.parameters[1], self.parameters[0]])
            target = target / np.sqrt(target.dot(target))
        else:
            hand = 'right'
            delta = 5
            target = target - np.array([0.0, -self.parameters[1], self.parameters[0]])
            target = target / np.sqrt(target.dot(target))

        # print 'target:', target
        # first, use current angel as initial guess
        init_guess = current_angles[delta:(delta+4)]
        res = self.point_certain_direction(target, hand, init_guess)
        # print(res.fun)
        if res.fun < 0.1:
            res_list.append(res)

        # then, generate random samples as initial guess
        for i in range(30):
            init_guess = np.random.rand(4)
            for j in range(4):
                init_guess[j] = self.links[j+delta].angle_limits[0] + \
                                init_guess[j] * (self.links[j+delta].angle_limits[1] -
                                                 self.links[j+delta].angle_limits[0])

            res = self.point_certain_direction(target, hand, init_guess)
            # print(res.fun)
            if res.fun < 0.1:
                res_list.append(res)

        # pick up the closest result
        if len(res_list) == 0:
            print("target point is not in workspace")
            current_angles = None
        else:
            min_diff = 100
            for a_res in res_list:
                diff = a_res.x - current_angles[delta:(delta+4)]
                diff_square = diff.dot(diff)
                if diff_square < min_diff:
                    min_diff = diff_square
                    final_res = a_res.x
            current_angles[delta:(delta+4)] = final_res
            # print current_angles
        return current_angles

    def point_certain_direction(self, target, hand, initial_angles=None):
        if hand == 'left':
            delta = 1
        else:
            delta = 5

        if initial_angles is None:
            x_temp = self.get_angles()
            x0 = x_temp[delta:(delta+4)]
        else:
            x0 = initial_angles

        bounds_temp = [(0, 0), (0, 0), (0, 0), (0, 0)]
        # set boundary
        for i in range(4):
            bounds_temp[i] = (self.links[i+delta].angle_limits[0], self.links[i+delta].angle_limits[1])

        # use optimization to solve inverse kinematics. the cost function is 'objective_inverse_kinematics'
        res = optimize.minimize(self.objective_point_certain_direction, x0, args=(target, hand),
                                bounds=bounds_temp, method='SLSQP')

        return res

    def objective_point_certain_direction(self, angles, target, hand):
        if hand == 'left':
            # left_hand
            for i in range(4):
                self.links[i+1].angle = angles[i]
            self.forward_kinematics()
            shoulder_l = np.array([0.0, self.parameters[1], self.parameters[0]])
            hand_l = self.calculate_point_position(4, [0, self.parameters[5], 0])
            direction = hand_l - shoulder_l
            normed_direction = direction / np.sqrt(direction.dot(direction))
            diff = target - normed_direction
        else:
            # right hand
            for i in range(4):
                self.links[i+5].angle = angles[i]
            self.forward_kinematics()
            shoulder_r = np.array([0.0, self.parameters[1], self.parameters[0]])
            hand_r = self.calculate_point_position(8, [0, -self.parameters[5], 0])
            direction = hand_r - shoulder_r
            normed_direction = direction / np.sqrt(direction.dot(direction))
            diff = target - normed_direction

        # value = diff.dot(diff)
        value = diff.dot(diff) + 0.01 * angles[3] * angles[3]
        return value

    def random_sample_point_direction_2(self, target, current_angles):
        current_angles = np.array(current_angles)
        current_angles = current_angles.astype(float)
        target = np.array(target)
        target = target.astype(float)

        res_list = list()
        # left_or_right = np.random.rand(1)
        left_or_right = [1]
        if left_or_right[0] >= 0.5:
            hand = 'left'
            delta = 1
            # target = target - np.array([0.0, self.parameters[1], self.parameters[0]])
            # target = target / np.sqrt(target.dot(target))
        else:
            hand = 'right'
            delta = 5
            # target = target - np.array([0.0, -self.parameters[1], self.parameters[0]])
            # target = target / np.sqrt(target.dot(target))

        # print 'target:', target
        # first, use current angel as initial guess
        init_guess = current_angles[delta:(delta+4)]
        res = self.point_certain_direction_2(target, hand, init_guess)
        # print(res.fun)
        if res.fun < 0.1:
            res_list.append(res)

        # then, generate random samples as initial guess
        for i in range(30):
            init_guess = np.random.rand(4)
            for j in range(4):
                init_guess[j] = self.links[j+delta].angle_limits[0] + \
                                init_guess[j] * (self.links[j+delta].angle_limits[1] -
                                                 self.links[j+delta].angle_limits[0])

            res = self.point_certain_direction_2(target, hand, init_guess)
            # print(res.fun)
            if res.fun < 0.1:
                res_list.append(res)

        # pick up the closest result
        if len(res_list) == 0:
            print("target point is not in workspace")
            current_angles = None
        else:
            min_diff = 100
            for a_res in res_list:
                diff = a_res.x - current_angles[delta:(delta+4)]
                diff_square = diff.dot(diff)
                if diff_square < min_diff:
                    min_diff = diff_square
                    final_res = a_res.x
            current_angles[delta:(delta+4)] = final_res
            # print current_angles
        return current_angles

    def point_certain_direction_2(self, target, hand, initial_angles=None):
        if hand == 'left':
            delta = 1
        else:
            delta = 5

        if initial_angles is None:
            x_temp = self.get_angles()
            x0 = x_temp[delta:(delta+4)]
        else:
            x0 = initial_angles

        bounds_temp = [(0, 0), (0, 0), (0, 0), (0, 0)]
        # set boundary
        for i in range(4):
            bounds_temp[i] = (self.links[i+delta].angle_limits[0], self.links[i+delta].angle_limits[1])

        # use optimization to solve inverse kinematics. the cost function is 'objective_inverse_kinematics'
        res = optimize.minimize(self.objective_point_certain_direction_2, x0, args=(target, hand),
                                bounds=bounds_temp, method='SLSQP')

        return res

    def objective_point_certain_direction_2(self, angles, target, hand):
        if hand == 'left':
            # left_hand
            for i in range(4):
                self.links[i+1].angle = angles[i]
            self.forward_kinematics()
            elbow_l = self.links[4].position
            hand_l = self.calculate_point_position(4, [0, self.parameters[5], 0])
            direction = hand_l - elbow_l
            normed_direction = direction / np.sqrt(direction.dot(direction))
            target_direction = target - elbow_l
            norm_target_direction = target_direction / np.sqrt(target_direction.dot(target_direction))
            diff = norm_target_direction - normed_direction
        else:
            # right hand
            for i in range(4):
                self.links[i+5].angle = angles[i]
            self.forward_kinematics()
            elbow_r = self.links[8].position
            hand_r = self.calculate_point_position(8, [0, -self.parameters[5], 0])
            direction = hand_r - elbow_r
            normed_direction = direction / np.sqrt(direction.dot(direction))
            target_direction = target - elbow_r
            norm_target_direction = target_direction / np.sqrt(target_direction.dot(target_direction))
            diff = norm_target_direction - normed_direction

        # value = diff.dot(diff)
        value = diff.dot(diff)
        return value



