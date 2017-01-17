# coding=utf-8
import random


def voice_ai(data):

    command_type = "voice_command"
    # generate sorry text
    if data is None:
        data_out = failed_understanding()
        return data_out, command_type
    # if something is heard
    else:
        return data, command_type


def failed_understanding():
        num = random.randint(1, 20)
        # switch case method in python
        text = {
            1: "抱歉,我听不懂你的指令",
            2: "我听不懂你说的话,你可以再说一遍吗",
            3: "不懂不懂嘛",
            4: "请你再说一遍好不好呀",
            5: "虽然我学富五车,可依然不能理解主人的意思",
            6: "我不理解您的意思",
            7: "嗨,你说的什么呀？",
            8: "你在说什么我完全听不懂,一点儿概念也没有",
            9: "主人,请你再说一遍好吗",
            10: "主人,请指示",
            11: "指示未收到,无法执行动作",
            12: "主人,我不能正确解析您的命令",
            13: "语句分析失败,请重试",
            14: "愧疚的我不知道该怎样开口,但是我听不懂",
            15: "请重试",
            16: "我不理解您的意思",
            17: "哎呦,你说的什么呀？",
            18: "你在说什么我完全听不懂,一点儿概念也没有",
            19: "主人,请你再说一遍好吗",
            20: "请重新发出指令"
         }.get(num)
        return text


