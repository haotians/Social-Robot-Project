# coding=utf-8
# Author: Honghua Liu, Last Modified Date: 2016-02-17
import time
import threading
import random
import socket
import wave
from bs4 import BeautifulSoup
import subprocess as sp
import os
import components.Components as Components
import PyVoiceInit as Pv


class Voice(Components.Node):
    def __init__(self, master_object):
        # init node type
        Components.Node.__init__(self, master_object)
        self.name = "voice_node"
        # init baidu API port
        self.API_KEY = 'UTGBR7UgGltonFz2XDRIIpoY'
        self.API_SECRET = 'ee54c5b505d02e99fab8d814816467b1'
        # init xunfei work path
        # work path listen
        self.xunfei_work_path_listen = self.get_file_path() + "/xunfeiAPI_listen/build/bin/"
        self.WAVE_OUTPUT_FILENAME = self.xunfei_work_path_listen + "wav/out.wav"
        # work path say
        self.xunfei_work_path_say = self.get_file_path() + "/xunfeiAPI_say/bin/"
        self.xunfei_lib_path_say = self.get_file_path() + "/xunfeiAPI_say/lib/"
        self.xunfei_sp = None

        # init two objects for listener and speaker
        self.recognizer = None
        self.microphone = None
        self.speak_flag = True

        self.CHANNELS = 1
        self.RATE = 16000
        # voice method switch
        self.use_baidu = True
        # ai_voice_input_flag
        self.input_thread_flag = False
        self.input_thread = None

    def __del__(self):
        self.stop_asr()

    def start_get_input_thread(self):
        self.input_thread = threading.Thread(target=self.get_input)
        self.input_thread.daemon = True
        self.input_thread_flag = True  # used to stop thread
        self.input_thread.start()  # start thread

    def stop_get_input_thread(self):
        self.input_thread_flag = False

    def get_input(self):
        while self.input_thread_flag:   # if listen and say
            # self.output_status_to_master(False)
            # check node status
            if self.thread_active is False:
                break
            # 1. get messages
            messages = self.get_messages_from_all_topics()
            if len(messages) > 0:
                print messages
            # 2. process messages
            self.process_messages(messages)
            # 3.output if necessary
            # 4.report to master
            self.output_status_to_master(False)
            time.sleep(0.01)

    def process_messages(self, messages):
        for message in messages:
            msg_time, msg_type, data, source = self.message_object.message_dewarp(message)
            # voice data is detected
            if msg_type == 5:
                # if start listen
                if self.recognizer is not None:
                    open_listen_flag = self.recognizer.return_listen_flag()
                    # disable recognizer
                    self.recognizer.check_status(False)
                    print "data in voice: ", data
                    self.say(data)
                    # self.say_baidu(data)
                    source = self.message_object._generate_source_type_id(source)
                    command = [self.message_object.message_warp(source, [2])]
                    self.output_all_messages(command)
                    if open_listen_flag:
                        # enable recognizer
                        self.recognizer.check_status(True)
            elif msg_type == 300:
                if data == 0:
                    self.recognizer.check_status(True)
                else:
                    self.recognizer.check_status(False)

    # get the file location for path configuration
    def get_file_path(self):
        return os.path.dirname(os.path.realpath(__file__))

    def say(self, txt):
        if self.use_baidu:
            self.say_baidu(txt)
        else:
            self.say_xunfei(txt)

    def say_baidu(self, txt, random_say=False):
        """
        Function: convert the content of the str_static to voice and then to broadcast it.
        :param txt:
        :type txt: str.
        :returns:
        """
        if not self.speak_flag:
            return
        # call baidu API
        tts = Pv.TTS(app_key=self.API_KEY, secret_key=self.API_SECRET)
        speed = 5
        pitch = 8
        vol = 5
        if random_say is True:
            speed = random.randint(2, 8)
            pitch = random.randint(3, 8)
            vol = random.randint(1, 9)
        tts.say(txt, speed, pitch, vol, 0)

    def say_xunfei(self, txt):
        # generate command to write file
        command_write = self.xunfei_work_path_say + "ttsdemo "+txt
        # lib_path
        path_setting = "export LD_LIBRARY_PATH=" + self.xunfei_lib_path_say + ":LD_LIBRARY_PATH;"
        # call xunfei API to generate wave file
        sp.call(path_setting + command_write, shell=True, cwd=self.xunfei_work_path_say)
        # wave file path
        say_file_path = self.xunfei_work_path_say + "text_to_speech_test.pcm"
        # play the wave file
        command_play = "ffplay -nodisp -autoexit " + say_file_path
        FNULL = open(os.devnull, 'w')
        sp.call(command_play, shell=True, cwd=self.xunfei_work_path_say)

    def create_recognizer(self):
        self.recognizer = Pv.Recognizer(app_key=self.API_KEY, secret_key=self.API_SECRET,
                                        energy_threshold=1500, dynamic_energy_threshold_flag=False)
        self.microphone = Pv.Microphone()

    def _node_run(self):
        if not self.use_baidu:
            self.run_asr()
            time.sleep(5)
        self.say("语音系统启动,请指示")
        # if start listen
        self.create_recognizer()

        # start input receiver
        self.start_get_input_thread()
        #  if start listen
        while self.thread_active:
            print "start listening..."

            with self.microphone as source:
                audio_data = self.recognizer.listen(source, None, 5, self.use_baidu)
            if audio_data is None:
                print "waiting for enable signal..."
                time.sleep(1)
                continue
            # this code helps ends the voice thread, no need to go to recognize_audio module
            if not self.thread_active:
                break
            # print "finish listening. start recognize audio..."
            self.recognize_audio(audio_data)
            time.sleep(0.01)
        print "listen while finish"

        self.say("语音系统关闭,再见")

        if not self.use_baidu:
            self.stop_asr()
        self.stop_get_input_thread()

    def recognize_audio(self, audio_data):
        # baidu recognize
        if self.use_baidu:
            try:
                text = self.recognizer.recognize(audio_data)
                self.baidu_text2commands(text)
            except LookupError:
                print("Could not understand audio")
                error_message = self.failed_understanding()
                self.failed_say(error_message)
        # xunfei recognize
        else:
            frames = list()
            frames.append(audio_data.data)
            wave_file = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
            wave_file.setnchannels(self.CHANNELS)
            wave_file.setsampwidth(2)  # waveFile.setsampwidth(audio.get_sample_size(FORMAT))
            wave_file.setframerate(self.RATE)
            wave_file.writeframes(b''.join(frames))
            wave_file.close()
            text, confidence = self.vsr_req()
            if confidence is None:
                print("Could not understand audio")
                error_message = self.failed_understanding()
                self.failed_say(error_message)
            else:
                confidence = int(confidence)
                if confidence > 40:
                    self.xufei_text2command(text)
                else:
                    print("Could not understand audio")
                    error_message = self.failed_understanding()
                    self.failed_say(error_message)

    def stop_thread(self):
        """
        Function: To update the global variable self.stop_thread_flag to be false.
        :return: stop_thread_flag
        """
        # stop the inner loops inside recognizer
        self.recognizer.check_status(False)
        # stop voice thread from core
        self.thread_active = False

    def run_asr(self):

        command_cp = "cp " + self.xunfei_work_path_listen + "wav/first_time_backup.wav " + self.xunfei_work_path_listen\
                     + "wav/out.wav"
        xun_fei_sp_cp = sp.Popen(command_cp, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,
                               cwd=self.xunfei_work_path_listen)
        xun_fei_sp_cp.kill()
        command_chmod = "chmod 777 " + self.xunfei_work_path_listen + "wav/out.wav"
        xun_fei_sp_chmod = sp.Popen(command_chmod, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,
                               cwd=self.xunfei_work_path_listen)
        xun_fei_sp_chmod.kill()
        time.sleep(1)

        command = self.xunfei_work_path_listen + "asr"
        self.xunfei_sp = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,
                                  cwd=self.xunfei_work_path_listen)

    def stop_asr(self):
        if self.xunfei_sp is not None:
            self.xunfei_sp.kill()
            self.xunfei_sp = None

    def vsr_req(self):
        encoding = "GBK"
        HOST = '0.0.0.0'            # The remote host
        # HOST = '127.0.0.1'            # The remote host  # netstat -atun | grep 8888
        PORT = 8888                 # The same port as used by the server
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5.0)
        s.connect((HOST, PORT))
        s.sendall('vsr')
        s.settimeout(None)
        time.sleep(0.05)
        try:
            data = s.recv(4096)
            print "=" * 80
            y = BeautifulSoup(data, "xml")
            try:
                text = y.rawtext.string
                confidence = y.confidence.string
                s.close()
                return text, confidence
            except AttributeError:
                s.close()
                return None, None
        except ArithmeticError:
            s.close()
            return None, None

    def set_node_status(self, useBaidu):
        self.use_baidu = useBaidu

    def update_voice_method(self, useBaidu=True):
        self.use_baidu = useBaidu

    def xufei_text2command(self, text=None):
        print "text=:", text
        wheel_data = None
        arm_data = None
        if cmp(text, u'向前')==0:
            wheel_data = [1, 0.5, 0.2, 0]
        elif cmp(text, u'向后')==0:
            wheel_data = [1, -0.5, 0.2, 0]
        elif cmp(text, u'向左')==0:
            wheel_data = [2, 0.5, 0, 0.1]
        elif cmp(text, u'向右')==0:
            wheel_data = [2, -0.5, 0, 0.1]
        elif cmp(text, u'手打开')==0:
            arm_data = [12, 0, 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0]
        elif cmp(text, u'手关闭')==0:
            arm_data = [11, 0, 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0]
        elif cmp(text, u'再见')==0:
            arm_data = [2, './data/arm_trajectory/back_wave', 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0]
        elif cmp(text, u'走开')==0:
            arm_data = [2, './data/arm_trajectory/finger_point', 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0]
        elif cmp(text, u'高兴')==0:
            arm_data = [2, './data/arm_trajectory/wave', 0, 0, 0, 0,  0, 0, 0, 0,  0, 0, 0]
        message = []
        if wheel_data is not None:
            message.append(self.message_object.message_warp('wheel_data', wheel_data))
            self.output_all_messages(message)
            print "msg to wheel:", message
        if arm_data is not None:
            message.append(self.message_object.message_warp('arm_data', arm_data))
            self.output_all_messages(message)
            print "msg to arm:", message
        self.output_status_to_master(False)

    def baidu_text2commands(self, text=None):
        print "text=:", text
        raw_commands = []
        if text.find(u"前") >= 0 or text.find(u"前进") >= 0 or text.find(u"向前") >= 0 or \
                        text.find(u"往前") >= 0 or text.find(u"钱") >= 0 :
            raw_commands = [1, 0.5, 0.2, 0]
        elif text.find(u"后") >= 0 or text.find(u"退") >= 0 or text.find(u"后退") >= 0 or \
                        text.find(u"往后") >= 0 or text.find(u"往回") >= 0 :
            raw_commands = [1, -0.5, 0.2, 0]
        elif text.find(u"左") >= 0 or text.find(u"左转") >= 0 or text.find(u"往左") >= 0 or \
                        text.find(u"靠左") >= 0 or text.find(u"左边") >= 0 :
            raw_commands = [2, 0.5, 0, 0.1]
        elif text.find(u"右") >= 0 or text.find(u"右转") >= 0 or text.find(u"往右") >= 0 or \
                        text.find(u"靠右") >= 0 or text.find(u"右边") >= 0 :
            raw_commands = [2, -0.5, 0, 0.1]
        elif text.find(u"停") >= 0 or text.find(u"停止") >= 0 or text.find(u"静止") >= 0 or \
                        text.find(u"不动") >= 0 or text.find(u"婷") >= 0 or text.find(u"庭") >= 0 or \
                        text.find(u"亭") >= 0:
            raw_commands = [0, 0, 0, 0]

        if len(raw_commands) > 0:
            commands = [self.message_object.message_warp("wheel_data", raw_commands, "voice")]
            print "commands in voice ", commands
            self.output_all_messages(commands)
            self.output_status_to_master(False)

    def failed_understanding(self):
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

        text = "..."
        return text

    def failed_say(self, error_message=None):
        num = random.randint(1, 10)
        if num <= 3:
            if error_message is not None:
                self.say(error_message)


if __name__ == '__main__':
    master = Components.Master()
    voice = Voice(master)
    voice.say_baidu('你们给我搞的这个东西……Excited')
