# coding=utf-8

from legacy import Basic


class CloudDeckControl(Basic.BasicCommand):
    def __init__(self):
        Basic.BasicCommand.__init__(self)

    def cloud_deck_turn_left(self, angle=None):
        # 轮子右转的同时，摄像头为了保持不变，必须左转 90
        print "摄像头左转 90:", angle

    def cloud_deck_turn_right(self, angle=None):
        # 轮子左转的同时，摄像头为了保持不变，必须右转 90
        print "摄像头右转 90:", angle