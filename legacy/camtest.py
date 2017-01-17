# import pygame.camera
# import pygame.image
#
#
# pygame.camera.init()
# cam = pygame.camera.Camera(pygame.camera.list_cameras()[0])
# cam.start()
# while True:
#     img = cam.get_image()
#     pygame.image.show("lol")

# os.system("ls")
# os.system("ffmpeg -s 320x240 -f video4linux2 -i /dev/video0 -f mpeg1video -b:a 800k -r 30 -filter:v "crop=200:200:60:20" http://139.129.130.13:9999/123/200/200/")
# -c copy -f avi -b:a 800k -r 30 lol3.avi
# ffmpeg -y -s 320x240 -f video4linux2 -i /dev/video0 -r 10 picture/pic%02d.jpg -vcodec mjpeg
# python -c "import os; fifo_read = open('outpipe', 'r', 0); print fifo_read.read().splitlines()[0]"
# web ui video port on Ali cloud
# ffmpeg -s 320x240 -f video4linux2 -i /dev/video0 -f mpeg1video -b:v 800k -r 30 http://123.57.176.245:8082/123/320/240/

FFMPEG_BIN = "ffmpeg" # on Linux ans Mac OS
import os
import time
import threading

import cv2

from library.vision.CameraSupport import CameraControl
import legacy.CVDetect


def start_cam():
    os.system("ffmpeg -s 320x240 -f video4linux2 -i /dev/video1 -f mpeg1video -r 30 pipe:1 > outpipe")


def extract(target):
    cap = cv2.VideoCapture()
    cap.open(target)
    print "read success!"
    fnum = 0
    while(True):
        # Capture frame-by-frame
        # print "loop"
        ret, frame = cap.read()
        if not ret:
            continue
        cv2.imshow("lol2",frame)
        cv2.waitKey(50)
        print fnum, "pts:", cap.get(cv2.cv.CV_CAP_PROP_POS_MSEC)
        fnum = fnum + 1
    # When everything done, release the capture
    cap.release()
    print "release cam"
    cv2.destroyAllWindows()

if __name__ == "__main__":
    command = [ FFMPEG_BIN,
                '-y',                  # overwrite existing file
                '-an',                 # disable audio recording
                '-f', 'video4linux2',  # input format
                '-i', '/dev/video0',   # input devices
                '-f', 'mpeg1video',
                '-s', '640*480',       # video frame
                '-b:a', '800k',        # biterate
                '-r', '30',             # fps
                'http://123.57.176.245:8082/123/320/240/',
                ]

    command2 = [ FFMPEG_BIN,
                '-i', 'lol2.avi',
                '-vcodec', 'png',
                '-f', 'image2pipe',
                '-']

    command3 = [ FFMPEG_BIN,
                '-y',                  # overwrite existing file
                '-an',                 # disable audio recording
                '-f', 'video4linux2',  # input format
                '-i', '/dev/video2',   # input devices
                '-r', '10',            # fps
                '-f', 'avi',
                '-s', '640*480',       # video frame
                'pipe:1 > outpipe'
                 ]


    command4 = [ FFMPEG_BIN,
                '-y',                  # overwrite existing file without asking
                '-an',                 # disable audio recording
                '-s', '320*240',       # video frame
                '-f', 'video4linux2',  # input format
                '-i', '/dev/video1',   # input devices
                '-r', '30',            # fps
                '-pix_fmt', 'rgb24',
                '-vcodec', 'rawvideo',
                '-f', 'image2pipe','-']

    face = legacy.CVDetect.FaceDetect()

    cam= CameraControl.CameraControl()
    cam.update_camera(True, 3, None)
    # cam.run_camera()
    t = threading.Thread(target=cam.run_camera)
    # t.daemon = True
    t.start()


    # print "camera run"
    # t2 = threading.Thread(target=face.face_detection)
    # t2.daemon = True
    # t2.start()
    # print "vision on"
    #
    # time.sleep(10)
    # print "sleep over"
    # face.stop_thread()
    # print "camera close"
    time.sleep(15)

    cam.stop_camera()
    print "over"

    # useful command
    # ffmpeg -s 320x240 -f video4linux2 -i /dev/video1 -f mpeg1video -b:a 800k -r 30 http://123.57.176.245:8082/123/320/240/ -f mpeg1video -b:v 64k -r 30 -y pipe:1 > outpipe


    # os.system("mkfifo outpipe")
    # command5 = "ffmpeg -f video4linux2 -i /dev/video0 -f avi -r 10 -y -s 640x480 pipe:1 > outpipe"
    # pipe = sp.Popen(command5, shell=True, stdout=sp.PIPE, stderr=sp.STDOUT)
    # print "pipe wait"
    # # pipe.wait()
    # print "now sleep"
    # time.sleep(10)
    # print "pipe kill"
    # pipe.kill()

    # os.system("ffmpeg -f video4linux2 -i /dev/video2 -f mpeg1video -b:v 64k -r 30 http://123.57.176.245:8082/123/320/240/ -f avi -r 10 -y -s 640x480 pipe:1 > outpipe")
    # os.system(command3)
    # sp.check_output(command3)

    # fifo_read = open('outpipe', 'r', 0)
    # print fifo_read.read().splitlines()

    # edit by lhh
    # ffmpeg -s 320x240 -f video4linux2 -i /dev/video1 -f mpeg1video -b:v 64k -r 30 http://123.57.176.245:8082/123/320/240/ -f mpeg1video -b:v 64k -r 30 -y pipe:1 > outpipe -f mpeg1video -b:v 64k -r 30 lhh.avi

