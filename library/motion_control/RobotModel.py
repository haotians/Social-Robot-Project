import numpy as np
from scipy import constants
from scipy import optimize

import OneLink


class RobotModel(object):
    '''
        this object define the kinematic model of the whole robot
        the robot have 11 links. one for main body, five links for each arm.
        For each arm, shoulder has three degrees of freedom, elbow has one degree of freedom,
        and hand has one freedom (which we don't use)
    '''

    def __init__(self):
        self.links = []

        self.links.append(OneLink.OneLink())
        self.links[0].index = 0
        self.links[0].name = 'base'
        self.links[0].angle = 0.0
        self.links[0].axis = np.array([0, 0, 1])
        self.links[0].offset = np.array([0.0, 0.0, 0.0])
        self.links[0].position = np.array([0.0, 0.0, 0.0])
        self.links[0].angle_limits = np.array([-constants.pi, constants.pi])
        self.links[0].orientation = np.eye(3)

        # link1 - link3 are left shoulder using x-z-x layout
        self.links.append(OneLink.OneLink())
        self.links[1].index = 1
        self.links[1].name = 'left_shoulder_1'
        self.links[1].parent = 0
        self.links[1].angle = 0.0
        self.links[1].axis = np.array([1, 0, 0])
        self.links[1].offset = np.array([-0.2, 0.0, 0.49])
        self.links[1].position = np.array([0.0, 0.0, 0.0])
        self.links[1].angle_limits = np.array([- 0.2 * constants.pi, 0.5 * constants.pi])
        self.links[1].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[2].index = 2
        self.links[2].name = 'left_shoulder_2'
        self.links[2].parent = 1
        self.links[2].angle = 0.0
        self.links[2].axis = np.array([0, 0, 1])
        self.links[2].offset = np.array([-0.06, 0.0, 0.0])
        self.links[2].position = np.array([0.0, 0.0, 0.0])
        self.links[2].angle_limits = np.array([-0.3 * constants.pi, 0.3 * constants.pi])
        self.links[2].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[3].index = 3
        self.links[3].name = 'left_shoulder_3'
        self.links[3].parent = 2
        self.links[3].angle = 0.0
        self.links[3].axis = np.array([1, 0, 0])
        self.links[3].offset = np.array([-0.05, 0.0, 0.0])
        self.links[3].position = np.array([0.0, 0.0, 0.0])
        self.links[3].angle_limits = np.array([- 0.5 * constants.pi, 0.1 * constants.pi])
        self.links[3].orientation = np.eye(3)

        # robot(4) is the left elbow
        self.links.append(OneLink.OneLink())
        self.links[4].index = 4
        self.links[4].name = 'left_elbow'
        self.links[4].parent = 3
        self.links[4].angle = 0.0
        self.links[4].axis = np.array([0, 1, 0])
        # self.links[4].offset = np.array([-0.175, 0.0, 0.0])
        self.links[4].offset = np.array([-0.20, 0.0, 0.0])
        self.links[4].position = np.array([0.0, 0.0, 0.0])
        self.links[4].angle_limits = np.array([0 * constants.pi, 0.5 * constants.pi])
        self.links[4].orientation = np.eye(3)

        # robot(5) is the left hand
        self.links.append(OneLink.OneLink())
        self.links[5].index = 5
        self.links[5].name = 'left_hand'
        self.links[5].parent = 4
        self.links[5].angle = 0.0
        self.links[5].axis = np.array([1, 0, 0])
        # self.links[5].offset = np.array([-0.695, 0.0, 0.0])
        self.links[5].offset = np.array([-0.33, 0.0, 0.0])
        self.links[5].position = np.array([0.0, 0.0, 0.0])
        self.links[5].angle_limits = np.array([-constants.pi / 2, constants.pi / 2])
        self.links[5].orientation = np.eye(3)

        # link6 - link8 are right shoulder using x-z-x layout
        self.links.append(OneLink.OneLink())
        self.links[6].index = 6
        self.links[6].name = 'right_shoulder_1'
        self.links[6].parent = 0
        self.links[6].angle = 0.0
        self.links[6].axis = np.array([1, 0, 0])
        self.links[6].offset = np.array([0.2, 0.0, 0.49])
        self.links[6].position = np.array([0.0, 0.0, 0.0])
        self.links[6].angle_limits = np.array([-0.2 * constants.pi, 0.5 * constants.pi])
        self.links[6].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[7].index = 7
        self.links[7].name = 'right_shoulder_2'
        self.links[7].parent = 6
        self.links[7].angle = 0.0
        self.links[7].axis = np.array([0, 0, 1])
        self.links[7].offset = np.array([0.06, 0.0, 0.0])
        self.links[7].position = np.array([0.0, 0.0, 0.0])
        self.links[7].angle_limits = np.array([-0.3 * constants.pi, 0.3 * constants.pi])
        self.links[7].orientation = np.eye(3)

        self.links.append(OneLink.OneLink())
        self.links[8].index = 8
        self.links[8].name = 'right_shoulder_3'
        self.links[8].parent = 7
        self.links[8].angle = 0.0
        self.links[8].axis = np.array([1, 0, 0])
        self.links[8].offset = np.array([0.05, 0.0, 0.0])
        self.links[8].position = np.array([0.0, 0.0, 0.0])
        self.links[8].angle_limits = np.array([-0.5 * constants.pi, 0.1 * constants.pi])
        self.links[8].orientation = np.eye(3)

        # robot(9) is the right elbow
        self.links.append(OneLink.OneLink())
        self.links[9].index = 9
        self.links[9].name = 'right_elbow'
        self.links[9].parent = 8
        self.links[9].angle = 0.0
        self.links[9].axis = np.array([0, 1, 0])
        # self.links[9].offset = np.array([0.175, 0.0, 0.0])
        self.links[9].offset = np.array([0.20, 0.0, 0.0])
        self.links[9].position = np.array([0.0, 0.0, 0.0])
        self.links[9].angle_limits = np.array([-0.5 * constants.pi, 0 * constants.pi])
        self.links[9].orientation = np.eye(3)

        # robot(10) is the right hand
        self.links.append(OneLink.OneLink())
        self.links[10].index = 10
        self.links[10].name = 'right_hand'
        self.links[10].parent = 9
        self.links[10].angle = 0.0
        self.links[10].axis = np.array([1, 0, 0])
        # self.links[10].offset = np.array([0.695, 0.0, 0.0])
        self.links[10].offset = np.array([0.33, 0.0, 0.0])
        self.links[10].position = np.array([0.0, 0.0, 0.0])
        self.links[10].angle_limits = np.array([-constants.pi / 2, constants.pi / 2])
        self.links[10].orientation = np.eye(3)

    def set_angles(self, angles):
        for i in range(len(self.links)):
            self.links[i].angle = angles[i]

    def get_angles(self):
        '''
        :return: angles of each link
        '''
        angles = np.zeros(len(self.links))
        for i in range(len(self.links)):
            angles[i] = self.links[i].angle
        return angles

    def generate_axis_angle_rotation_matrix(self, axis, angle):
        '''
        generate axis angle rotation matrix
        it is a common formulation of axis-angle representation
        :param axis: rotation angle
        :param angle: angle
        :return: rotation matrix
        '''
        c = np.cos(angle)
        s = np.sin(angle)
        t = 1 - c

        axis_length = 0
        for i in range(3):
            axis_length = axis_length + axis[i] * axis[i]

        axis = axis / np.sqrt(axis_length)
        x = axis[0]
        y = axis[1]
        z = axis[2]

        result = np.array([[t*x*x + c,   t*x*y - z*s, t*x*z + y*s],
                           [t*x*y + z*s, t*y*y + c,   t*y*z - x*s],
                           [t*x*z - y*s, t*y*z + x*s, t*z*z + c]])
        return result

    def forward_kinematics(self):
        '''
        this function calculate forward kinematics. It generates the position and angle of each link one by one
        This is the standard way to do forward kinematic
        '''
        # the base have no parent
        self.links[0].rotation = self.generate_axis_angle_rotation_matrix(self.links[0].axis,self.links[0].angle)
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
        '''
        inverse kinematics. use simple 'sqp' method to find angles.
        :param target_l: left hand position
        :param target_r: right hand position
        '''

        if initial_angles is None:
            # the initial guess use current angles
            x0 = self.get_angles()
        else:
            x0 = initial_angles
        # set boundaries of optimization
        bounds_temp = [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]
        for i in range(len(self.links)-1):
            bounds_temp[i] = (self.links[i+1].angle_limits[0], self.links[i+1].angle_limits[1])
        # use optimization to solve inverse kinematics. the cost function is 'objective_inverse_kinematics'
        res = optimize.minimize(self.objective_inverse_kinematics, x0[1:len(self.links)], args=(target_l, target_r),
                                bounds=bounds_temp, method='SLSQP')
        # update angles
        for i in range(len(self.links)-1):
            self.links[i+1].angle = res.x[i]
        # update positions
        self.forward_kinematics()
        return res

    def objective_inverse_kinematics(self, angles, target_l, target_r):
        '''
        the cost/objective function for inverse kinematics.
        the cost is the square of the difference between targets and hands
        :param angles: current angles
        :param target_l: target of left hand
        :param target_r: target of right hand
        :return: costs
        '''
        # set angles
        for i in range(len(self.links)-1):
            self.links[i+1].angle = angles[i]
        # use forward kinematics to find the position of hands
        self.forward_kinematics()
        # calculate the difference
        hand_l = target_l - self.links[5].position
        hand_r = target_r - self.links[10].position
        # the square of difference
        value1 = hand_l.dot(hand_l)
        value2 = hand_r.dot(hand_r)
        # returen costs
        return value1 + value2

    def random_sample_ik(self, target, current_angles):
        current_angles = np.array(current_angles)
        res_list = list()
        # first, use current angel as initial guess
        if target[0] >= 0:
            # right hand
            init_guess = current_angles[6:10]
        else:
            init_guess = current_angles[1:5]
        res = self.one_hand_inverse_kinematics(target, init_guess)
        print(res.fun)
        if res.fun < 0.001:
            res_list.append(res)
        # then, generate random samples as initial guess
        for i in range(30):
            init_guess = np.random.rand(4)
            if target[0] >= 0:
                # right hand
                for j in range(4):
                    init_guess[j] = self.links[j+6].angle_limits[0] + \
                                    init_guess[j] * (self.links[j+6].angle_limits[1] - self.links[j+6].angle_limits[0])
            else:
                # left hand
                for j in range(4):
                    init_guess[j] = self.links[j+6].angle_limits[0] + \
                                    init_guess[j] * (self.links[j+1].angle_limits[1] - self.links[j+1].angle_limits[0])
            res = self.one_hand_inverse_kinematics(target, init_guess)
            print(res.fun)
            if res.fun < 0.01:
                res_list.append(res)
        # pick up the closest result
        if len(res_list) == 0:
            print("target point is not in workspace")
            current_angles = None
        else:
            if target[0] >= 0:
                # right hand
                min_diff = 100
                for a_res in res_list:
                    diff = a_res.x - current_angles[6:10]
                    diff_square = diff.dot(diff)
                    if diff_square < min_diff:
                        min_diff = diff_square
                        final_res = a_res.x
                current_angles[6:10] = final_res
            else:
                # right hand
                min_diff = 100
                for a_res in res_list:
                    diff = a_res.x - current_angles[1:5]
                    diff_square = diff.dot(diff)
                    if diff_square < min_diff:
                        min_diff = diff_square
                        final_res = a_res.x
                current_angles[1:5] = final_res
        return current_angles

    def one_hand_inverse_kinematics(self, target, initial_angles=None):

        if initial_angles is None:
            # the initial guess use current angles
            x_temp = self.get_angles()
            if target[0] >= 0:
                x0 = x_temp[6:10]
            else:
                x0 = x_temp[1:5]
        else:
            x0 = initial_angles

        bounds_temp = [(0, 0), (0, 0), (0, 0), (0, 0)]
        if target[0] >= 0:
            # right hand
            for i in range(4):
                bounds_temp[i] = (self.links[i+6].angle_limits[0], self.links[i+6].angle_limits[1])
        else:
            # left hand
            for i in range(4):
                bounds_temp[i] = (self.links[i+1].angle_limits[0], self.links[i+1].angle_limits[1])
        # use optimization to solve inverse kinematics. the cost function is 'objective_inverse_kinematics'
        res = optimize.minimize(self.objective_inverse_kinematics_one_hand, x0, args=(target, 1),
                                bounds=bounds_temp, method='SLSQP')

        return res

    def objective_inverse_kinematics_one_hand(self, angles, target, temp):
        if target[0] < 0:
            # left_hand
            for i in range(4):
                self.links[i+1].angle = angles[i]
            self.forward_kinematics()
            diff = target - self.links[5].position
        else:
            # right hand
            for i in range(4):
                self.links[i+6].angle = angles[i]
            self.forward_kinematics()
            diff = target - self.links[10].position

        value = diff.dot(diff)
        return value

