#!/usr/bin/env python
import os
import sys
import getopt
import time 
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True
### Add load path
base = os.path.dirname(__file__)
if '' == base:
    base = '.'
sys.path.append('%s/../'%base)

from cascade import *
from utils   import *

def usage():
    print("-----------------------------------------------")
    print('[[Usage]]::')
    print('\t%s [Paras] train.model test.jpg'%(sys.argv[0]))
    print("[[Paras]]::")
    print("\thelp|h : Print the help information ")
    print("-----------------------------------------------")
    return 


def detect_jpg_2(detector, jpg_path):

    if not os.path.exists(jpg_path):
        raise Exception("Image not exist:"%(jpg_path))

    img_I = Image.open(jpg_path)#.convert('L')
    img = cv2.imread(jpg_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    cv2.imshow("result", img)
    cv2.waitKey(10)
    # src_img.show()
    # time.sleep(1)
    # if src_img.mode == 'L':
    #     img = src_img
    # else:
    #     img = src_img.convert("L")
    # img = src_img.convert('L')

    # print "boom"
    maxSide = 200.0
    w, h = img_I.size
    scale = max(1, max(w/maxSide, h/maxSide))
    ws = int(w/scale + 0.5)
    hs = int(h/scale + 0.5)
    # print ws, hs
    # out = img.resize((100,100))
    # img = img.resize((ws,hs), Image.NEAREST)
    # img = img.resize((ws,hs))
    face_reshape = cv2.resize(gray, (ws,hs), interpolation = cv2.INTER_CUBIC)
    imgArr = np.asarray(face_reshape).astype(np.uint8)
    print imgArr.shape

    time_b = time.time()
    rects, confs = detector.detect(imgArr, 1.1, 2)
    t = getTimeByStamp(time_b, time.time(), 'sec')
    # print rects, confs


    ### TODO: Use NMS to merge the candidate rects and show the landmark, Now merge the rects with opencv,
    res = cv2.groupRectangles(rects, 3, 0.2)
    rects = res[0]

    print rects[0]
    [x,y,w,h] = rects[0]
    print x,y,w,h

    ### Show Result
    # draw = ImageDraw.Draw(img)
    for i in xrange(len(rects)):
        [x,y,w,h] = rects[i]
        draw_face(gray, (x,y,w+x,y+h))
        # draw.rectangle((rects[i][0],
        #                 rects[i][1],
        #                 rects[i][0]+rects[i][2],
        #                 rects[i][1]+rects[i][3]),
        #                outline = "red")
    cv2.imshow("result", gray)
    cv2.waitKey(0)
    print("Detect time : %f s"%t)
    # img.show()
    #########################################

    if len(rects) > 0:
        num, _ = rects.shape
        for i in xrange(num):
            rects[i][0] = int(rects[i][0]*scale +0.5)
            rects[i][1] = int(rects[i][1]*scale +0.5)
            rects[i][2] = int(rects[i][2]*scale +0.5)
            rects[i][3] = int(rects[i][3]*scale +0.5)
    return


def draw_face(dst, (x0, y0, x1, y1)):
    # draw name
    # cv2.putText(dst, txt, (x0-20, y0-20), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 0), lineType=cv2.CV_AA)
    # draw distance
    # cv2.putText(dst, distance, (x0-20, y0), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 0), lineType=cv2.CV_AA)
    # Draw the face area in image:
    cv2.rectangle(dst, (x0, y0),(x1,y1), (0,255,0), 2)
    cv2.waitKey(10)
    
def main(argv):
    try:
        options, args = getopt.getopt(argv, 
                                      "h", 
                                      ["help"])
    except getopt.GetoptError:  
        usage()
        return
    
    if len(argv) < 2:
        usage()
        return

    for opt , arg in options:
        if opt in ('-h', '--help'):
            usage()
            return
    
    detector = JointCascador()  
    detector = detector.loadModel(args[0])    
    detect_jpg(detector, args[1])    


def detect_jpg(detector, jpg_path):
    if not os.path.exists(jpg_path):
        raise Exception("Image not exist:"%(jpg_path))

    src_img = Image.open(jpg_path)
    if 'L' != src_img.mode:
        img = src_img.convert("L")
    else:
        img = src_img

    maxSide = 200.0
    w, h = img.size
    scale = max(1, max(w/maxSide, h/maxSide))
    ws = int(w/scale + 0.5)
    hs = int(h/scale + 0.5)
    img = img.resize((ws,hs), Image.NEAREST)
    imgArr = np.asarray(img).astype(np.uint8)

    time_b = time.time()
    rects, confs = detector.detect(imgArr, 1.1, 2)
    t = getTimeByStamp(time_b, time.time(), 'sec')

    ### TODO: Use NMS to merge the candidate rects and show the landmark, Now merge the rects with opencv,
    res = cv2.groupRectangles(rects, 3, 0.2)
    rects = res[0]

    ### Show Result
    draw = ImageDraw.Draw(img)
    for i in xrange(len(rects)):
        draw.rectangle((rects[i][0],
                        rects[i][1],
                        rects[i][0]+rects[i][2],
                        rects[i][1]+rects[i][3]),
                       outline = "red")

    print("Detect time : %f s"%t)
    img.show()
    #########################################

    if len(rects) > 0:
        num, _ = rects.shape
        for i in xrange(num):
            rects[i][0] = int(rects[i][0]*scale +0.5)
            rects[i][1] = int(rects[i][1]*scale +0.5)
            rects[i][2] = int(rects[i][2]*scale +0.5)
            rects[i][3] = int(rects[i][3]*scale +0.5)
    return


def test():

    detector = JointCascador()
    # detector = detector.loadModel("train.model")
    detector = detector.load_model("face.pyobj")
    detect_jpg(detector, "test.jpg")

if __name__ == '__main__' :
    test()
    # main(sys.argv[1:])
