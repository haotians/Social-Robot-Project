from __future__ import division
import Tkinter as tk
# allows moving dots with multiple selection.
import CVDetect as  cd
# import voice_reco as vcr
from library import gui as fpp

import library.vision.facedetect.facedetectyl as fyl

# temp
from voice_temp import *

SELECTED_COLOR = "red"
UNSELECTED_COLOR = "blue"


class MainGUI(tk.Frame):
# class MainGUI(object):
    ###################################################################
    ###### Event callbacks for THE CANVAS (not the stuff drawn on it)
    ###################################################################
    # def mouseDown(self, event):
    #     # see if we're inside a dot. If we are, it
    #     # gets tagged as CURRENT for free by tk.

    #     if not event.widget.find_withtag(CURRENT):
    #         # we clicked outside of all dots on the canvas. unselect all.

    #         # re-color everything back to an unselected color
    #         self.draw.itemconfig("selected", fill=UNSELECTED_COLOR)
    #         # unselect everything
    #         self.draw.dtag("selected")
    #     else:
    #         # mark as "selected" the thing the cursor is under
    #         self.draw.addtag("selected", "withtag", CURRENT)
    #         # color it as selected
    #         self.draw.itemconfig("selected", fill=SELECTED_COLOR)

    #     self.lastx = event.x
    #     self.lasty = event.y


    def createWidgets(self):
        self.QUIT = tk.Button(self.Frame1, text='QUIT', foreground='red',
                           command=self.quit, width=10)

        self.face_check = tk.BooleanVar()
        self.upperbody_check = tk.BooleanVar()

        self.cv_c1 = tk.Checkbutton(self.Frame1, text = "Face", variable =self.face_check, \
                         onvalue = 1, offvalue = 0, height=5, \
                         width = 20)
        self.cv_c2 = tk.Checkbutton(self.Frame1, text = "Video", variable = self.upperbody_check, \
                         onvalue = 1, offvalue = 0, height=5, \
                         width = 20)

        ################
        # make the canvas and bind some behavior to it
        ################
        # self.draw = tk.Canvas(self, width="5i", height="5i")
        # tk.Widget.bind(self.draw, "<1>", self.mouseDown)
        # tk.Widget.bind(self.draw, "<B1-Motion>", self.mouseMove)

        # and other things.....
        # self.button = tk.Button(self, text="make a new dot", foreground="blue",
        #                      command=self.makeNewDot)
        self.button_cv = tk.Button(self.Frame1, text="opencv", foreground="blue",
                        command=self.button_opencv, width=10)

        self.bn_voice = tk.Button(self.Frame1, text="voice", foreground="blue",
                        command=self.button_voice, width=10)

        self.bn_fpp = tk.Button(self.Frame1, text="face++", foreground="blue",
                        command=self.button_fpp, width=10)

        message = "EwayBot: Vision and voice"
        self.label = tk.Message(self.Frame2, width="10i", text=message)

        self.menubar.add_command(label="file")
        self.menubar.add_command(label="options")

        self.label.pack(side=tk.TOP, fill=tk.X)


        self.button_cv.pack(side=tk.TOP, fill=tk.X)

        self.bn_voice.pack(side=tk.TOP, fill=tk.X)
        self.bn_fpp.pack(side=tk.TOP, fill=tk.X)
        self.cv_c1.pack(side=tk.TOP, fill=tk.Y)
        self.cv_c2.pack(side=tk.TOP, fill=tk.Y)
        self.QUIT.pack(side=tk.BOTTOM, fill=tk.Y)

        # self.draw.pack(side=tk.LEFT)

        # config the txtbox and scoll bar
        self.log_txt = tk.Text(self.Frame2, height=15, width=55)
        scr = tk.Scrollbar(self.Frame2)
        scr.config(command=self.log_txt.yview)
        self.log_txt.config(yscrollcommand=scr.set)
        scr.pack(side="right", fill="y", expand=False)
        self.log_txt.config(state=tk.DISABLED)
        self.log_txt.pack(side=tk.TOP,fill="both", expand=True)
        self.log_txt.config(state=tk.NORMAL)
        self.log_txt.insert(tk.INSERT, "Hello, welcome to EwayBot \n")
        self.log_txt.config(state=tk.DISABLED)
        # voice_tts_th("Hello, welcome to EwayBot")

    def __init__(self, master=None):
        root = tk.Tk()
        root.geometry("640x480+15+150")
        self.menubar = tk.Menu(root)

        root.config(menu=self.menubar)
        tk.Frame.__init__(self, root)
        self.Frame1 = tk.Frame(master, bg="white",relief=tk.RIDGE, borderwidth=5)
        self.Frame1.pack(side=tk.LEFT, fill=tk.BOTH,)
        # self.Frame1.grid(row = 0, column = 0, rowspan = 3, columnspan = 2,
        #                 sticky=tk.W+tk.E+tk.N+tk.S)
        self.Frame2 = tk.Frame(master, bg='snow',relief=tk.RIDGE, borderwidth=5)
        # self.Frame2.grid(row = 2, column = 0, rowspan = 3, columnspan = 2,
        #                     sticky=tk.W+tk.E+tk.N+tk.S)
        self.Frame2.pack(side=tk.LEFT, fill=tk.BOTH)
        # tk.Pack.config(self)
        self.createWidgets()
        self.pack()
        self.cd=cd.FaceDetect()
        self.fpp = fpp.FaceppLib()
        self.fyl=fyl.FaceDetect()

    def button_opencv(self):
        print "test cv"
        self.log_txt.config(state=tk.NORMAL)
        self.log_txt.insert(tk.INSERT, "Camera On\n")
        self.log_txt.config(state=tk.DISABLED)
        t=threading.Thread(target=self.cd.faceDetection)
        # t = threading.Thread(target=self.fyl.faceDetection)
        t.daemon=True
        t.start()
        # warning=fyl.warning
        # self.log_txt.config(state=tk.NORMAL)
        # self.log_txt.insert(tk.INSERT, warning+"\n")
        # self.log_txt.config(state=tk.DISABLED)
        # t.join()
        # print fyl.filenames
        # print fyl.distances.items()
        # for f,d in fyl.distances.items():
        # # for f,d in cd.distances.items():
        #     filename =f
        #     distance_gui=d
        #     if not os.path.isfile(filename):
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, "file not exist please capture\n")
        #         self.log_txt.config(state=tk.DISABLED)
        #         return
        #     res, detect = self.fpp.verify(img_file=filename)
        #     if detect is not None:
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, "Person detected\n")
        #         self.log_txt.insert(tk.INSERT,"The distance between the camera and the person is %f meters."%distance_gui+"\n")
        #         age = str(detect['face'][0]['attribute']['age']['value'])
        #         race = (detect['face'][0]['attribute']['race']['value'])
        #         happiness = str(detect['face'][0]['attribute']['smiling']['value']/100)
        #         print race, happiness
        #         person_att = ("Age: " + age + ", Race: " + race  + ", Happiness: "+ happiness+"\n")
        #         self.log_txt.insert(tk.INSERT, person_att)
        #         self.log_txt.config(state=tk.DISABLED)
        #     if res is not None:
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, res+", how are doing? \n")
        #         self.log_txt.config(state=tk.DISABLED)
        #         voice_tts_th(res+", Hello, how are doing?")
        #     else:
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, "Nobody Detected or not in database")
        #         self.log_txt.config(state=tk.DISABLED)


    def button_voice(self):
        pass
        # don't delete the next code for backup
        # i = 0
        # while i<=3:
        #     i = i + 1
        #     res = vcr.voice_in()
        #     self.log_txt.config(state=tk.NORMAL)
        #     self.log_txt.insert(tk.INSERT, "voice CMD:"+res+"\n")
        #     self.log_txt.config(state=tk.DISABLED)
        #     if res.find("camera")>=0 and res.find("open")>=0:
        #         self.button_opencv()
        #         break
        #     if res.find("face") >= 0 and res.find("track")>=0:
        #         self.cv_c1.select()
        #     if res.find("body") >= 0 and res.find("track")>=0:
        #         self.cv_c2.select()
        #     if res.find("detect")>=0 and res.find("face")>=0:
        #         self.button_fpp()
        #         break
        #     if res.find("voice") >= 0 and res.find("off") >= 0:
        #         break
        #
        # self.log_txt.config(state=tk.NORMAL)
        # self.log_txt.insert(tk.INSERT, "Exit voice CMD\n")
        # self.log_txt.config(state=tk.DISABLED)


    def button_fpp(self):
        pass
        # don't delete the next code for backup
        # # for f,d in fyl.copyDistances.items():
        # for f,d in fyl.distances.items():
        # # for f,d in cd.distances.items():
        #     filename =f
        #     distance_gui=d
        #     if not os.path.isfile(filename):
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, "file not exist please capture\n")
        #         self.log_txt.config(state=tk.DISABLED)
        #         return
        #     res, detect = self.fpp.verify(img_file=filename)
        #     if detect is not None:
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, "Person detected\n")
        #         self.log_txt.insert(tk.INSERT,"The distance between the camera and the person is %f meters."%distance_gui+"\n")
        #         age = str(detect['face'][0]['attribute']['age']['value'])
        #         race = (detect['face'][0]['attribute']['race']['value'])
        #         happiness = str(detect['face'][0]['attribute']['smiling']['value']/100)
        #         print race, happiness
        #         person_att = ("Age: " + age + ", Race: " + race  + ", Happiness: "+ happiness+"\n")
        #         self.log_txt.insert(tk.INSERT, person_att)
        #         self.log_txt.config(state=tk.DISABLED)
        #     if res is not None:
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, res+", how are doing? \n")
        #         self.log_txt.config(state=tk.DISABLED)
        #         voice_tts_th(res+", Hello, how are doing?")
        #     else:
        #         self.log_txt.config(state=tk.NORMAL)
        #         self.log_txt.insert(tk.INSERT, "Nobody Detected or not in database \n")
        #         self.log_txt.config(state=tk.DISABLED)
if __name__ == '__main__':
    # root = tk.Tk()
    # root.geometry("800x480+15+150")
    # test = MainGUI(root)
    test = MainGUI()
    test.mainloop()