#!/usr/bin/python

# coding=utf-8


import pyttsx
import time
import threading


def voice_tts(msg):
    engine = pyttsx.init()
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate-80)
    engine.say_baidu(msg)
    engine.runAndWait()


def voice_tts_th(msg):
    # t = threading.Thread(target=voice_tts, args=[msg])
    t = threading.Thread(target=voice_tts(msg))
    t.daemon = True
    t.start()

if __name__ == '__main__':
    voice_tts_th("how are you yan shuai")
