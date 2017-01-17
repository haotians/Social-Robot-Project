# coding=utf-8

from __future__ import division
import threading
import time

from legacy import Basic
import CloudDeck as cloud_deck


class Track(Basic.BasicCommand):
    def __init__(self):
        Basic.BasicCommand.__init__(self)
        self.speed = 150
        self.cloud_deck = cloud_deck.CloudDeckControl()

    # angle > 0
    def once_turn_right(self, angle=None, radius=None):
        # 1.轮子开始运动前,轮子原地右转90，摄像头左转90
        turn_angle = 90
        t1 = threading.Thread(target=self.cloud_deck.cloud_deck_turn_left, args=(turn_angle,))
        t1.daemon = True
        t1.start()
        time.sleep(0.001)
        # 轮子原地右转 wheel turn right 90
        print "轮子原地右转:角度是-90,旋转半径是0"

        # 2.轮子运动过程中，轮子逆时针做角度是Q,旋转半径是r的运动;摄像头保持不变，也就是始终与机器人运动方向垂直
        print "角度是Q,旋转半径是r:", angle, radius

        # 3.轮子到达目的地停止后,轮子左转90，摄像头右转90
        stop_turn_angle = 90
        t2 = threading.Thread(target=self.cloud_deck.cloud_deck_turn_right, args=(stop_turn_angle,))
        t2.daemon = True
        t2.start()
        time.sleep(0.001)
        # 轮子原地左转 wheel turn left 90
        print "轮子原地左转:角度是90,旋转半径是0", stop_turn_angle

    # angle < 0
    def once_turn_left(self, angle=None, radius=None):
        # 1.轮子开始运动前,轮子原地左转90，摄像头右转90
        turn_angle = 90
        t1 = threading.Thread(target=self.cloud_deck.cloud_deck_turn_right, args=(turn_angle,))
        t1.daemon = True
        t1.start()
        time.sleep(0.001)
        # 轮子原地左转 wheel turn right 90
        print "轮子原地左转:角度是90,旋转半径是0"

        # 2.轮子运动过程中，轮子顺时针做角度是Q,旋转半径是r的运动;摄像头保持不变，也就是始终与机器人运动方向垂直
        print "角度是-Q,旋转半径是r:", -angle, radius

        # 3.轮子到达目的地停止后,轮子右转90，摄像头左转90
        stop_turn_angle = 90
        t2 = threading.Thread(target=self.cloud_deck.cloud_deck_turn_left, args=(stop_turn_angle,))
        t2.daemon = True
        t2.start()
        time.sleep(0.001)
        # 轮子原地右转 wheel turn left 90
        print "轮子原地右转:角度是-90,旋转半径是0"
