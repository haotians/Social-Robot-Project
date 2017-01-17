# Standalone Voice Recognition Module

---
## Requirement

pyaudio
 `sudo apt-get install python-pyaudio`

beautifulsoup4 (for xml parsing)
 `pip install beautifulsoup4`

## Note

Though the server supports multi-thread, only one voice recognition module is running, so avoid sending request at the same time

[bnf grammer examples](http://bbs.xfyun.cn/forum.php?mod=viewthread&tid=11994&highlight=bnf)

## How to Build It
---
**make sure you changed the xunfei app id**

**make sure you are using 64bit xunfei lib if you are using a 64 bit OS**

goto the project folder

    mkdir build
    cd build
    cmake ../
    make


**then copy the bin folder to build folder (merge with the existing bin folder)**

## How to Run it

**make sure port 8888 is available**

 1. goto the `/build/bin` folder, run `python py_asr.py`
 2. wait for the first 2 recognition to be done ( about 5 secs)
 3. goto `/py` folder, run `sudo python py_clinet.py`
 4. recording your command 



