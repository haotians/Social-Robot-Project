#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import struct
import pyaudio
import wave
import sys
import time
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
 
def rec_audio():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1024
    RECORD_SECONDS = 2
    WAVE_OUTPUT_FILENAME = "../build/bin/wav/out.wav"
     
    audio = pyaudio.PyAudio()
     
    # start Recording
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                    rate=RATE, input=True,
                    frames_per_buffer=CHUNK)
    print "recording..."
    frames = []
     
    for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
        data = stream.read(CHUNK)
        frames.append(data)
    print "finished recording"
     
     
    # stop Recording
    stream.stop_stream()
    stream.close()
    audio.terminate()
     
    waveFile = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    waveFile.setnchannels(CHANNELS)
    waveFile.setsampwidth(audio.get_sample_size(FORMAT))
    waveFile.setframerate(RATE)
    waveFile.writeframes(b''.join(frames))
    waveFile.close()

def vsr_req():
    encoding = "GBK"

    HOST = '0.0.0.0'    # The remote host
    PORT = 8888              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(5.0)
    s.connect((HOST, PORT))
    s.sendall('vsr')
    # data = s.recv(1024)
    # # s.close()
    # print 'Received', repr(data)
    # data = s.recv(1024)
    # # s.close()
    # print 'Received', repr(data)
    data = s.recv(4096)
    print "=" * 80 
    print data
    # print "repr(data) is ", repr(data)
    # myint = struct.unpack("!i", data)[0]
    # print "退出"
    y = BeautifulSoup(data, "xml")
    # print y
    print "=" * 80 
    try:
        print "raw txt:", y.rawtext.string
        print "confidence:", y.confidence.string
    except Exception, e:
        print "no Results"


    s.close()

if __name__ == '__main__':
    t0 = int(round(time.time() * 1000))
    # rec_audio()
    t1 = int(round(time.time() * 1000))
    print "=" * 80 
    print "# audio recording :", t1-t0, " ms"
    print "=" * 80 
    vsr_req()
    t2 = int(round(time.time() * 1000))
    print "=" * 80 
    print "# recognition :", t2-t1, " ms"
    print "=" * 80 
