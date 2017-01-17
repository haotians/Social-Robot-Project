# Author: Haotian Shi, Last Modified Date: 2016-02-17
# Author: Yehang Liu, Last Modified Date: 2016-02-17
# Author: Honghua Liu, Last Modified Date: 2016-03-01
import subprocess as sp
import cv2


class CameraControl(object):

    # os.system("ffmpeg -f video4linux2 -i /dev/video2 -f mpeg1video -b:v 64k -r 30 http://123.57.176.245:8082/123/320/240/ -f avi -r 10 -y -s 640x480 pipe:1 > outpipe")
    # 'ffmpeg', '-s', '320x240', '-f', 'video4linux2', '-i', '/dev/video0', '-f', 'mpeg1video', '-b:v', '800k', '-r', '30', 'http://192.168.1.128:' + self.cam_stream_port + '/123/320/240/'
    def __init__(self):

        # True : camera on, False: camera off
        self.status = False
        # 1,close; 2, webUI only; 3, local vision only; 4, webUI + local vision
        self.mode = 1
        self.uiport = None
        self.face_pipe = None
        self.cam_number = 0

    def update_camera(self, status, mode, uiport, cam_number=None):
        self.status = status
        self.mode = mode
        # update ui port when necessary
        if uiport is not None:
            self.uiport = "http://123.57.176.245:"+ uiport + "/123/320/240/"
        if cam_number is not None:
            self.cam_number = cam_number

    def run_camera(self):
        command = self._generate_command()
        print command
        if command is None:
            self.status = False
            return
        else:
            self.face_pipe = sp.Popen(command, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)

    # this method can't work, leave it here for the time being
    def stop_camera(self):
        if self.face_pipe is not None:
            self.face_pipe.kill()
            self.face_pipe = None

    def _generate_command(self):

        # exec is required or pipe.kill() won't work at all
        command_input = "exec ffmpeg -f video4linux2 -i /dev/video" + str(self.cam_number) + " "
        command_webui = "-f mpeg1video -s 320x240 -b:v 64k -r 30 " + self.uiport + " "
        command_localface = "-f avi -r 10 -y -s 640x480 pipe:1 > outpipe "

        if self.mode == 3:
            return command_input+command_webui
        elif self.mode == 2:
            return command_input+command_localface
        elif self.mode == 4:
            return command_input+command_webui+command_localface
        else:
            return None


def open_camera(video, size=None, pipe=None):
    """
    :param size: video size, default is 640*480
    :param pipe: name of the pipe if pipe is used
    :return: video object you wanna play
    """
    if size is None:
        # size = [1280, 720]

        # Modified by Yehang Liu
        # change normal camera captured size back to vgg format

        size = [640, 480]
    if pipe is None:
        video = cv2.VideoCapture(0)
    else:
        video = cv2.VideoCapture(pipe)
    # self.video = cv2.VideoCapture("outpipe")
    video.set(3, size[0])
    video.set(4, size[1])
    return video


def release_camera(video):
    video.release()
    cv2.destroyAllWindows()


