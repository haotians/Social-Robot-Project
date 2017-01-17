# coding=utf-8
import random

def response_api(text_in):

    if cmp(text_in,'鱼') == 0:
        text_out = response_fish()
    elif cmp(text_in,'花盆') == 0:
        text_out = response_flowerpot()
    elif cmp(text_in,'汉堡') == 0:
        text_out = "这个汉堡我吃不了,不过还是谢谢你"
    elif cmp(text_in,'文字') == 0:
        text_out = response_word()
    else:
        text_out = "我看到了" + text_in
    return text_out

def response_word():
    num = random.randint(1, 8)
    # switch case method in python
    text = {
        1: "抱歉,我暂时还不能理解你们的文字",
        2: "我还是个小孩子,我看不懂",
        3: "这本书好像很好吃的样子...",
        4: "我发现了一段有趣的文字",
        5: "我的二进制传输系统,比这个高级多了",
        6: "啊,我发现了一段有趣的文字",
        7: "啊,我发现了一段有趣的文字",
        8: "啊,我发现了一段有趣的文字",
     }.get(num)
    return text


def response_flowerpot():
    num = random.randint(1, 8)
    # switch case method in python
    text = {
        1: "花花草草,最有爱啦",
        2: "这个花盆充满了生机",
        3: "我爱这一猪盆栽...",
        4: "我发现了一个花盆,快来瞧瞧",
        5: "一花一世界,一叶一菩提",
        6: "啊,我发现了一个花盆",
        7: "我看到了一个花盆",
        8: "我看到了一个花盆",
     }.get(num)
    return text


def response_hamburger():
    num = random.randint(1, 8)
    # switch case method in python
    text = {
        1: "我最喜欢的汉堡包,谢谢你主人",
        2: "我看到了一个汉堡",
        3: "我看到了一个汉堡",
        4: "我发现了一个汉堡",
        5: "汉堡,汉堡,吃了就饱",
        6: "这个汉堡是给我吃得吗",
        7: "我看到了一个汉堡",
        8: "我看到了一个汉堡",
     }.get(num)
    return text

def response_fish():
    num = random.randint(1,5)
    # switch case method in python
    text = {
        1: "我看见了一条鱼",
        2: "我看见了一条鱼",
        3: "我看见了一条鱼",
        4: "我看见了一条鱼",
     }.get(num)
    return text

