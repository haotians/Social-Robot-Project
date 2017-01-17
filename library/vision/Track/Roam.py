# coding=utf-8
import time
import components.Components as Components
import random
import numpy as np
import math


class Para(object):
    def __init__(self):
        self.position = np.array([500, 500])
        self.direction = 0
        self.v_max = 10
        self.a_max = 0.1
        self.kp = 0.1
        self.ka = 0.1
        self.is_obs = 0
        self.is_move = 0
        self.contact_dis = 25
        self.distance = 0


class GenerateMap(object):
    def __init__(self):
        self.map_range = np.array([1000, 1000])
        self.obstacle_r = 100
        self.obstacle_num = 5
        self.map_result = []

    def gene_map(self):
        """
        r = rand()*radius/2 + radius/2;
        center = range*0.1 + rand(1,2).*range*0.9;
        :return: map_result
        """
        for i in range(self.obstacle_num):
            r = random.random() * self.obstacle_r / 2 + self.obstacle_r / 2
            e1 = np.array([[0.1, 0], [0, 0.1]])
            e2 = np.array([[0.9, 0], [0, 0.9]])
            a = np.dot(self.map_range, e1)
            b = np.dot(self.map_range, e2)
            c = np.array([[random.random(), 0], [0, random.random()]])
            center = a + np.dot(b, c)
            r_m = [r, center]
            self.map_result.append(r_m)
        return self.map_result


class Roam(Components.Node):
    def __init__(self, master_object):
        Components.Node.__init__(self, master_object)
        self.para_object = Para()
        self.generate_map = GenerateMap()
        self.m = self.generate_map.gene_map()
        print "step map is:", self.m

    def set_goal(self, map_range=None):
        d = random.random() * map_range[0] / 5 + map_range[0] / 5
        theta_d = self.para_object.direction + math.pi / 2 + random.random() * math.pi / 2
        if theta_d > math.pi * 2:
            theta_d -= math.pi * 2
        goal = np.zeros(2)

        goal[0] = self.para_object.position[0] + d * math.cos(theta_d)
        if goal[0] < 10:
            goal[0] = 10
        elif goal[0] > map_range[0] - 10:
            goal[0] = map_range[0] - 10

        goal[1] = self.para_object.position[1] + d * math.sin(theta_d)
        if goal[1] < 10:
            goal[1] = 10
        elif goal[1] > map_range[1] - 10:
            goal[1] = map_range[1] - 10
        x_d = [x-y for x, y in zip(goal, self.para_object.position)]
        self.para_object.distance = np.linalg.norm(x_d)
        print "step set goal:", goal, theta_d
        return goal, theta_d

    def compute_velocity(self, goal=None, theta_d=None):
        v_err = [x-y for x, y in zip(goal, self.para_object.position)]
        mol = 1 / np.linalg.norm(v_err)
        e_mol = np.array([[mol, 0], [0, mol]])
        v_mol = np.dot(v_err, e_mol)
        d_err = theta_d - self.para_object.direction
        if d_err >= 0.1 or d_err <= -0.1:
            p_dis = np.zeros(2)
            a_dis = self.para_object.ka * d_err
            if a_dis > self.para_object.a_max:
                a_dis = self.para_object.a_max * d_err / abs(d_err)
            self.para_object.is_move = 0
        else:
            a_dis = 0
            e_kp = np.array([[self.para_object.kp, 0], [0, self.para_object.kp]])
            p_dis = np.dot(v_err, e_kp)
            if np.linalg.norm(p_dis) > self.para_object.v_max:
                e_v_max = np.array([[self.para_object.v_max, 0], [0, self.para_object.v_max]])
                p_dis = np.dot(v_mol, e_v_max)
            self.para_object.is_move = 1
        v = np.array([p_dis[0], p_dis[1], a_dis])
        print "step 1 computer velocity:", v
        return v

    def move(self, v=None):
        self.para_object.position = self.para_object.position + np.array([v[0], v[1]])
        self.para_object.direction = self.para_object.direction + v[2]
        if self.para_object.direction > math.pi * 2:
            self.para_object.direction -= math.pi * 2
        elif self.para_object.direction < -math.pi * 2:
            self.para_object.direction += math.pi * 2
        num_obs = len(self.m)
        for i in range(num_obs):
            dis_obs = np.linalg.norm(self.para_object.position - self.m[i][1])
            if dis_obs <= (self.m[i][0] + self.para_object.contact_dis) or self.para_object.position[0] < 0 or self.para_object.position[0] > 1000 or self.para_object.position[1] < 0 or self.para_object > 1000:
                if self.para_object.is_move == 1:
                    self.para_object.is_obs = 1
        print "step 2 move"

    def _node_run(self):
        while self.thread_active:
            messages = self.get_messages_from_all_topics()
            commands = None
            for i in range(len(messages)):
                commands = self.process_messages()  # process messages
            if commands is not None:
                self.output_all_messages(commands)
            self.output_status_to_master(False)
            time.sleep(0.01)

    def process_messages(self):
        for i in range(15):
            k = 0
            goal, theta_d = self.set_goal(self.generate_map.map_range)
            self.para_object.is_obs = 0
            while self.para_object.distance > 10 and k < 100 and self.para_object.is_obs == 0:
                v = self.compute_velocity(goal, theta_d)
                self.move(v)
                k += 1
        return 0  # just for test, maybe need to modify

    def for_backup(self):
        # def matrixMul(A, B):
        #     res = [[0] * len(B[0]) for i in range(len(A))]
        #     for i in range(len(A)):
        #         for j in range(len(B[0])):
        #             for k in range(len(B)):
        #                 res[i][j] += A[i][k] * B[k][j]
        #     return res
        #
        # def matrixMul2(A, B):
        #     return [[sum(a * b for a, b in zip(a, b)) for b in zip(*B)] for a in A]

        # a = [[1,2], [3,4], [5,6], [7,8]]
        # b = [[1,2,3,4], [5,6,7,8]]
        #
        # print matrixMul(a,b)
        # print matrixMul(b,a)
        # print "-"*90
        #
        # print matrixMul2(a,b)
        # print matrixMul2(b,a)
        # print "-"*90
        #
        # from numpy import dot
        # print map(list,dot(a,b))
        # print map(list,dot(b,a))

        # Out:
        # [[11, 14, 17, 20], [23, 30, 37, 44], [35, 46, 57, 68], [47, 62, 77, 92]]
        # [[50, 60], [114, 140]]
        # ------------------------------------------------------------------------------------------
        # [[11, 14, 17, 20], [23, 30, 37, 44], [35, 46, 57, 68], [47, 62, 77, 92]]
        # [[50, 60], [114, 140]]
        # ------------------------------------------------------------------------------------------
        # [[11, 14, 17, 20], [23, 30, 37, 44], [35, 46, 57, 68], [47, 62, 77, 92]]
        # [[50, 60], [114, 140]]
        pass

if __name__ == '__main__':
    master = Components.Master()
    roam = Roam(master)
    message = roam.process_messages()
    print message
