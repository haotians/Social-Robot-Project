# coding=utf-8
import time
import random
import socket
import wave
from bs4 import BeautifulSoup
import subprocess as sp
import os

import PyVoiceInit as Pv
import legacy.Basic


class EWayVoice(legacy.Basic.BasicCommand):
    """

    """
    def __init__(self):
        legacy.Basic.BasicCommand.__init__(self)
        # self.API_KEY = 'KWDnbPePMm5GfAV1Z2Et1ai1'
        # self.API_SECRET = 'd8f23d71249de2cb19a4c62f0018dba1'
        self.API_KEY = 'UTGBR7UgGltonFz2XDRIIpoY'
        self.API_SECRET = 'ee54c5b505d02e99fab8d814816467b1'
        self.listen_flag = True
        self.audio = None
        # self.res = ""
        self.recognizer = None
        self.microphone = None
        self.speak_flag = True
        # work path listen
        self.xunfei_work_path_listen = self.get_file_path() + "/xunfeiAPI_listen/build/bin/"
        self.WAVE_OUTPUT_FILENAME = self.xunfei_work_path_listen + "wav/out.wav"
        # work path say
        self.xunfei_work_path_say = self.get_file_path() + "/xunfeiAPI_say/bin/"
        self.xunfei_lib_path_say = self.get_file_path() + "/xunfeiAPI_say/lib/"
        self.CHANNELS = 1
        self.RATE = 16000
        self.xunfei_sp = None
        # baidu for default
        self.use_baidu = True

    def __del__(self):
        self.stop_asr()

    def say_baidu(self, txt, random_say=False):
        """
        Function: convert the content of the str_static to voice and then to broadcast it.
        :param txt:
        :type txt: str.
        :returns:
        """
        if not self.speak_flag:
            return
        tts = Pv.TTS(app_key=self.API_KEY, secret_key=self.API_SECRET)
        speed = 5
        pitch = 8
        vol = 5
        if random_say is True:
            speed = random.randint(2, 8)
            pitch = random.randint(3, 8)
            vol = random.randint(1, 9)
        tts.say(txt, speed, pitch, vol, 0)

    def say_xunfei(self,txt):

        command_write = self.xunfei_work_path_say + "ttsdemo "+txt
        path_setting = "export LD_LIBRARY_PATH=" + self.xunfei_lib_path_say + ":LD_LIBRARY_PATH;"
        print path_setting
        print command_write
        sp.call(path_setting + command_write, shell=True, cwd = self.xunfei_work_path_say)
        chunk = 1024

        say_file_path = self.xunfei_work_path_say + "text_to_speech_test.pcm"
        command_play = "ffplay -nodisp -autoexit "+ say_file_path
        FNULL = open(os.devnull, 'w')
        sp.call(command_play,shell = True, cwd = self.xunfei_work_path_say)



        # say_file_path = self.xunfei_work_path_say + "text_to_speech_test.pcm"
        # wf = wave.open(say_file_path, 'rb')
        #
        # p = pyaudio.PyAudio()
        #
        # # write the wav file
        # stream = p.open(format = p.get_format_from_width(wf.getsampwidth()),
        #                 channels = wf.getnchannels(),
        #                 rate = wf.getframerate(),
        #                 output = True)
        # time.sleep(0.01)
        #
        # # play the wav file
        # while True:
        #     data = wf.readframes(chunk)
        #     if data == "":
        #         break
        #     stream.write(data)
        #
        # stream.close()
        # p.terminate()

        # sp_write.kill()

    def say(self, txt):
        if self.use_baidu:
            self.say_baidu(txt)
        else:
            self.say_xunfei(txt)

    def create_recognizer(self):
        self.recognizer = Pv.Recognizer(app_key=self.API_KEY, secret_key=self.API_SECRET,
                                        energy_threshold=2000, dynamic_energy_threshold_flag=False)

        self.microphone = Pv.Microphone()
        self.listen_flag = True

    def voice_detect(self):
        # method = 0, Baidu
        # method = 1, kedaxunfei

        if not self.use_baidu:
            self.run_asr()
            # self.xunfei_sp = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)

        self.say_baidu("语音系统启动，请指示")
        self.create_recognizer()
        while self.listen_flag:
            text = ""
            print "start listening"
            with self.microphone as source:
                # self.audio = self.recognizer.listen(source, start_timeout=None, end_timeout=5)
                self.audio = self.recognizer.listen(source, None, 5, self.use_baidu)
            # this code helps ends the voice thread
            if not self.listen_flag:
                break

            print "recognize audio..."
            # baidu yuyin
            if self.use_baidu:
                try:
                    text = self.recognizer.recognize(self.audio)
                    print("You said " + text)
                    self.voice_control(text)
                except LookupError:
                    print("Could not understand audio")
                    self.failed_understanding()
                    continue
            # xunfei yuyin
            else:
                frames = list()
                frames.append(self.audio.data)
                wave_file = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
                wave_file.setnchannels(self.CHANNELS)
                wave_file.setsampwidth(2)  # waveFile.setsampwidth(audio.get_sample_size(FORMAT))
                wave_file.setframerate(self.RATE)
                wave_file.writeframes(b''.join(frames))
                wave_file.close()
                text, confidence = self.vsr_req()
                if confidence is not None and confidence >40:
                    print "I said: ", text
                    print "confidence: ", confidence
                    self.say(str(text))
                else:
                    print("Could not understand audio")
                    self.failed_understanding()
                # print("You said " + text)
        if self.use_baidu:
            self.stop_asr()

    def audio_in(self, *args):
        """
        Function: To recorded the speech content with microphone as source
        :param args: As the flag of the function(record(source, args[0])args[0] is the time how long to record.)
        :type args: List
        :return: To update the global variable (self.r).
        """
        self.audio = None
        self.recognizer = Pv.Recognizer(app_key=self.API_KEY, secret_key=self.API_SECRET)
        with Pv.Microphone() as source:                # use the default microphone as the audio source
            self.recognizer.adjust_for_ambient_noise(source)
            self.audio = self.recognizer.record(source, args[0])

        print "audio stop"
        with open('test.wav', 'w') as f:
            f.write(self.audio.data)

    def recognize_audio(self, *args):
        """
        Function: To convert the speech content to words
        :param args: As the flag of the function(record(source, args[0]))
        :type args: List
        :return: The audio recognized result (self.res).
        :type self.res:str
        """
        print args[0]
        time.sleep(args[0])
        self.res = " "
        try:
            self.res = self.recognizer.recognize(self.audio)
            print("You said " + self.res)    # recognize speech using BaiDu Speech Recognition
        except LookupError:                            # speech is unintelligible
            print("Could not understand audio")

        return self.res

    def vsr_req(self):
        encoding = "GBK"

        HOST = '0.0.0.0'            # The remote host
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

    def stop_thread(self):
        """
        Function: To update the global variable self.stop_thread_flag to be false.
        :return: stop_thread_flag
        """
        # stop voice thread from core
        self.listen_flag = False
        # stop the inner loops inside recognizer
        self.recognizer.check_status(False)

    def return_command(self):
        """
        Function: To find the keyword in the content of the voice.
        :return:
        """
        # command = self.voice_control()
        # return command
        # self.voice_control()
        pass

    def voice_control(self, text):
        """
        """
        if text.find(u"前") >= 0 or text.find(u"前进") >= 0 or text.find(u"向前") >= 0 or \
                        text.find(u"往前") >= 0 or text.find(u"钱") >= 0 :
            self.wheel_forward(5000)
            # value = 0
            # return value
        elif text.find(u"后") >= 0 or text.find(u"退") >= 0 or text.find(u"后退") >= 0 or \
                        text.find(u"往后") >= 0 or text.find(u"往回") >= 0 :
            self.wheel_backward()
            # value = 1
            # return value
        elif text.find(u"左") >= 0 or text.find(u"左转") >= 0 or text.find(u"往左") >= 0 or \
                        text.find(u"靠左") >= 0 or text.find(u"左边") >= 0 :
            self.wheel_turnleft()
            # value = 2
            # return value
        elif text.find(u"右") >= 0 or text.find(u"右转") >= 0 or text.find(u"往右") >= 0 or \
                        text.find(u"靠右") >= 0 or text.find(u"右边") >= 0 :
            self.wheel_turnright()
            # value = 3
            # return value
        elif text.find(u"停") >= 0 or text.find(u"停止") >= 0 or text.find(u"静止") >= 0 or \
                        text.find(u"不动") >= 0 or text.find(u"婷") >= 0 or text.find(u"庭") >= 0 or \
                        text.find(u"亭") >= 0:
            self.wheel_stop()
            # value = 4
            # return value
        elif text.find(u"挥") >= 0 or text.find(u"手") >= 0 or text.find(u"挥手") >= 0 or \
                        text.find(u"回首") >= 0:
            self.arm_build_in(4)
            # value = 11
            # return value
        elif text.find(u"摆") >= 0 or text.find(u"臂") >= 0 or text.find(u"摆臂") >= 0 :
            self.arm_build_in(3)
            # value = 12
            # return value

        elif text.find(u"关机位置") >= 0 or text.find(u"关机") >= 0 or text.find(u"变耶稣") >= 0:
            self.arm_build_in(5)

        elif text.find(u"预备位置") >= 0 or text.find(u"预备") >= 0 or text.find(u"初始位置") >= 0:
            self.arm_build_in(1)

        elif text.find(u"启动自毁程序") >= 0 or text.find(u"自毁程序") >= 0 or text.find(u"自杀") >= 0.\
                or text.find(u"去死") >= 0:
            self.wheel_stop()
            self.say_baidu("十,9,8,7,6,5,4,3,2,1. 我选择死亡")
            self.voice_off()

        elif text.find(u"闭嘴") >= 0 or text.find(u"别说话") >= 0 or text.find(u"少废话") >= 0:
            self.speak_flag = False

        elif text.find(u"和我说话") >= 0 or text.find(u"说话") >= 0 or text.find(u"聊天") >= 0:
            self.speak_flag = True

        elif text.find(u"关闭摄像机") >= 0 or text.find(u"停止摄像") >= 0 or text.find(u"瞎子") >= 0:
            self.camera_off()

        elif text.find(u"启动网络摄像") >= 0 or text.find(u"网络监控") >= 0 or text.find(u"监控") >= 0:
            self.camera_on_ui()

        elif text.find(u"启动人脸识别") >= 0 or text.find(u"人脸识别") >= 0 or text.find(u"人脸") >= 0:
            self.camera_on_local()

        elif text.find(u"启动摄像") >= 0 or text.find(u"摄像") >= 0 or text.find(u"开始摄像") >= 0:
            self.camera_on_ui_local()

        else:
            self.wheel_stop()
            self.failed_understanding()
            # value = -1
            # return value

    def failed_understanding(self):
        num = random.randint(1, 20)
        # switch case method in python
        value = {
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
        self.say(value)

    def run_asr(self):
        command = self.xunfei_work_path_listen + "asr"
        print command
        self.xunfei_sp = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT,cwd = self.xunfei_work_path_listen)

    def stop_asr(self):
        if self.xunfei_sp is not None:
            self.xunfei_sp.kill()
            self.xunfei_sp = None

    def get_file_path(self):
        return os.path.dirname(os.path.realpath(__file__))

    def update_voice_method(self, useBaidu = True):
        self.use_baidu = useBaidu

if __name__ == '__main__':
    voice = EWayVoice()
    # voice.say("I spent too much time outside")
    # voice.say("ok!1,2")
    voice.say_xunfei('我很抱歉，我今天是作为一个长者给你们这样讲。我不是新闻工作者，但是我见得太多了，我有这个必要告诉你们一点人生的经验')
    # voice.say_xunfei('人呐就都不知道,自己就不可以预料.一个人的命运啊,当然要靠自我奋斗,但是也要考虑到历史的行程')
    # voice.update_voice_method(False)
    # voice.voice_detect()

    # voice.failed_understanding(9)
