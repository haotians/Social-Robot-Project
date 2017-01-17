# coding=utf-8
from __future__ import division
import Tkinter as Tk
import pygame
import time
import threading

from library.voice import PyVoice as voice
from legacy import Core


class MainGUI(Tk.Frame):
    def _create_widgets(self):
        self.vv_label = Tk.Message(self.frame_vision_voice, width="5i", text="vision and voice")
        self.button_cv = Tk.Button(self.frame_vision_voice, text="视觉", command=self._button_open_cv,
                                   foreground="blue", height=self.height, width=self.width)
        self.bn_voice = Tk.Button(self.frame_vision_voice, text="自我介绍", command=self._button_voice,
                                  foreground="blue", height=self.height, width=self.width)


        self.bn_voice_control = Tk.Button(self.frame_vision_voice, text="语音",
                                          foreground="blue",  height=self.height, width=self.width)
        self.bn_voice_control.bind("<ButtonPress>", self._button_voice_record)
        self.bn_voice_control.bind("<ButtonRelease>", self._button_voice_recognize)

        self.vv_label.pack(side=Tk.TOP)
        self.button_cv.pack(side=Tk.TOP)
        self.bn_voice.pack(side=Tk.TOP)
        self.bn_voice_control.pack(side=Tk.TOP)

    def _create_arm_control_widgets(self):
        self.arm_label = Tk.Message(self.frame_arm, width="5i", text="Arms Controller")

        self.bn_gesture_wave = Tk.Button(self.frame_arm, text="挥手", command=self._button_gst_wave,
                                         foreground="blue", height=self.height, width=self.width)
        self.bn_gesture_swing = Tk.Button(self.frame_arm, text="摆臂", command=self._button_gst_swing,
                                          foreground="blue", height=self.height, width=self.width)
        self.QUIT = Tk.Button(self.frame_arm, text='退出', command=self._button_quit,
                              foreground='red', height=self.height, width=self.width)

        self.arm_label.pack(side=Tk.TOP)
        self.bn_gesture_wave.pack(side=Tk.TOP)
        self.bn_gesture_swing.pack(side=Tk.TOP)
        self.QUIT.pack(side=Tk.TOP)

    def _create_wheel_control_widgets(self):
        self.wheel_label = Tk.Message(self.frame_wheel, width="5i", text=" Wheels Controller")
        self.wheel_label.grid(row=1, column=1, padx=5, pady=10)
        self.bn_forward = Tk.Button(self.frame_wheel, text="前进", command=self._button_forward,
                                    foreground="blue", height=self.height, width=self.width)
        self.bn_forward.grid(row=2, column=2, padx=5, pady=10)
        self.bn_left_turn = Tk.Button(self.frame_wheel, text="左转", command=self._button_turn_left,
                                      foreground="blue", height=self.height, width=self.width)
        self.bn_left_turn.grid(row=3, column=1, padx=5, pady=10)
        self.bn_stop = Tk.Button(self.frame_wheel, text="停止", command=self._button_stop,
                                 foreground="blue", height=self.height, width=self.width)
        self.bn_stop.grid(row=3, column=2, padx=5, pady=10)
        self.bn_right_turn = Tk.Button(self.frame_wheel, text="右转", command=self._button_turn_right,
                                       foreground="blue", height=self.height, width=self.width)
        self.bn_right_turn.grid(row=3, column=3, padx=5, pady=10)
        self.bn_backward = Tk.Button(self.frame_wheel, text="后退", command=self._button_backward,
                                     foreground="blue", height=self.height, width=self.width)
        self.bn_backward.grid(row=4, column=2, padx=5, pady=1)

    def __init__(self, master=None):
        self.root = Tk.Tk()
        self.root.geometry("340x410+0+0")
        self.root.title("操作界面")
        self.width = 10
        self.height = 2
        self.border_width = 1

        Tk.Frame.__init__(self, self.root)
        self.frame_top = Tk.Frame(master, bg="white", relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_top.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.frame_left = Tk.Frame(self.frame_top, bg="snow", relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_left.pack(side=Tk.LEFT)

        self.frame_right = Tk.Frame(self.frame_top, bg="snow", relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_right.pack(side=Tk.RIGHT)

        self.frame_vision_voice = Tk.Frame(self.frame_left, bg="snow", relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_vision_voice.pack(side=Tk.TOP)

        self.frame_arm = Tk.Frame(self.frame_right, bg="snow", relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_arm.pack(side=Tk.RIGHT)

        self.frame_bottom = Tk.Frame(master, bg="white", relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_bottom.pack(side=Tk.TOP, fill=Tk.BOTH)

        self.frame_wheel = Tk.Frame(self.frame_bottom, bg='snow', relief=Tk.RIDGE, borderwidth=self.border_width)
        self.frame_wheel.pack(side=Tk.TOP)

        self._create_widgets()
        self._create_arm_control_widgets()
        self._create_wheel_control_widgets()
        self.pack()

        self.voice = voice.EWayVoice()
        self.start_time = float(0)
        self.time_for_record = float(2)

        self.core = Core.Core()
        self.core.start_mechanical_system()
        self.t_listen = threading.Thread(target=self.core._listen_command)
        self.t_listen.daemon = True
        self.t_listen.start()
        self.arm_data = [0, 0, 0, 0, 0, 0, 0]
        self.wheel_data = [0, 0, 0, 0, 0, 0]

    def _button_open_cv(self):
        self.core.start_local_vision_system()

    def _button_voice(self):
        # self.url = "/home/bot/ewayGit/vision/gui/test/"
        self.url = "/home/haotians/Documents/Github_Files/ewayGit/vision/gui/test/"
        pygame.mixer.init()
        pygame.mixer.music.load(self.url + "thy2.mp3")
        t = threading.Thread(target=pygame.mixer.music.play())
        t.daemon = True
        t.start()

    def _button_voice_record(self, event=None):
        # self.core.start_voice_system()

        t = threading.Thread(target=self.voice.audio_in, args=(self.time_for_record, ))
        t.daemon = True
        t.start()
        # self.voice.audio_in(self.time_for_record)
        self.start_time = time.time()

    def _button_voice_recognize(self, event=None):
        # self.core.start_voice_system()

        end_time = time.time()
        diff_time = end_time - self.start_time
        left_time = self.time_for_record - diff_time
        if left_time <= 0:
            left_time_float = float(self.time_for_record / 4)
        elif left_time < self.time_for_record / 2:
            left_time_float = float(self.time_for_record / 2)
        else:
            left_time_float = float(self.time_for_record)
        self.voice.recognize_audio(left_time_float)
        print "voice command exe"
        self._voice_command()

    def _button_gst_wave(self):
        self._clear_data()
        self.arm_data = [4, 0, 0, 0, 0, 0, 0]
        self._out_command(self.arm_data, self.wheel_data)

    def _button_gst_swing(self):
        self._clear_data()
        self.arm_data = [3, 0, 0, 0, 0, 0, 0]
        self._out_command(self.arm_data, self.wheel_data)

    def _button_forward(self):
        self._clear_data()
        self.wheel_data = [200, 150, 3, 200, 150, 3]
        self._out_command(self.arm_data, self.wheel_data)

    def _button_backward(self):
        self._clear_data()
        self.wheel_data = [200, 150, 2, 200, 150, 2]
        self._out_command(self.arm_data, self.wheel_data)

    def _button_turn_left(self):
        self._clear_data()
        self.wheel_data = [60, 100, 3, 60, 100, 2]
        self._out_command(self.arm_data, self.wheel_data)

    def _button_turn_right(self):
        self._clear_data()
        self.wheel_data = [60, 100, 2, 60, 100, 3]
        self._out_command(self.arm_data, self.wheel_data)

    def _button_stop(self):
        self._clear_data()
        self.wheel_data = [0, 0, 1, 0, 0, 1]
        self.arm_data = [5, 0, 0, 0, 0, 0, 0]
        self._out_command(self.arm_data, self.wheel_data)

    def _voice_command(self):
        command = self.voice.return_command()
        print "command:", command
        self._command_operate(command)

    def _command_operate(self, command):
        if command == 0:
            self._button_forward()
        elif command == 1:
            self._button_backward()
        elif command == 2:
            self._button_turn_left()
        elif command == 3:
            self._button_turn_right()
        elif command == 4:
            self._button_stop()
        elif command == 11:
            self._button_gst_wave()
        elif command == 12:
            self._button_gst_swing()
        elif command == -1:
            pass

    def _out_command(self, arm_data, wheel_data):
        self.core.get_data_old_gui(arm_data, wheel_data)

    def _clear_data(self):
        self.arm_data = [0, 0, 0, 0, 0, 0, 0]
        self.wheel_data = [0, 0, 0, 0, 0, 0]

    def _button_quit(self):
        self._clear_data()
        self.arm_data = [5, 0, 0, 0, 0, 0, 0]
        self._out_command(self.arm_data, self.wheel_data)
        time.sleep(1)
        self.core.kill_all_system()
        self.destroy()
        self.quit()

if __name__ == '__main__':
    test = MainGUI()
    test.mainloop()
