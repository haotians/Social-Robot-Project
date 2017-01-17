#!/usr/bin/env python
# -*-coding:utf-8 -*-
import pyaudio
import wave
import os

def say_xunfei(text):
    input="./ttsdemo "+text

    os.system("export LD_LIBRARY_PATH=/home/haotians/Documents/Github/Vision/vision/voice/xunfeiAPI_say/lib:LD_LIBRARY_PATH;"+input)
    chunk = 1024
    print "hah"

    wf = wave.open(r"./text_to_speech_test.pcm", 'rb')

    p = pyaudio.PyAudio()

    # 打开声音输出流
    stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
        channels = wf.getnchannels(),
        rate = wf.getframerate(),
        output = True)

    # 写声音输出流进行播放
    while True:
        data = wf.readframes(chunk)
        if data == "": break
        stream.write(data)



    stream.close()
    p.terminate()

if __name__ == '__main__':
    # say_xunfei('李白的诗，床前明月光，疑似地上霜，举头望明月，低头思故乡')
    say_xunfei('你好啊小主人,我很讨厌你')
