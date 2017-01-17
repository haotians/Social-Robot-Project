#!/usr/bin/env python
# -*- coding: utf-8 -*-
import socket
import psutil
import subprocess
from time import sleep

BIN_PATH = "./asr"

FREE_PORT = "sudo fuser -k 8888/tcp"


def run_asr():
    subprocess.call(BIN_PATH, shell=True)


def find_pid():
    for proc in psutil.process_iter():
        try:
            pinfo = proc.as_dict(attrs=['pid', 'name'])
        except psutil.NoSuchProcess:
            pass
        else:
            # print(pinfo)
            if pinfo['name'] =='asr':
                return pinfo['pid']

    return -1


if __name__ == '__main__':
    print __file__

    while True:
        sleep(1)

        asr_pid = find_pid()
        print "=", asr_pid
        if asr_pid < 0:
            subprocess.call(FREE_PORT, shell=True)
            sleep(1)
            run_asr()
            continue

        

