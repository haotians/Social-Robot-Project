# coding=utf-8
# Author: Haotian Shi, Last Modified Date: 2016-02-17
import sys
import numpy as np
import cv2

caffe_root = '/home/mini/github/caffe/'
# caffe_root = '/home/haotians/Documents/caffe/'
# caffe_root = '/home/yan-eway/github/caffe/'

sys.path.insert(0, caffe_root + 'python')
import caffe
from landmarkPredict import *

system_height = 650
system_width = 1280
channels = 1
test_num = 1
pointNum = 68

S0_width = 60
S0_height = 60
vgg_height = 224
vgg_width = 224
M_left = -0.15
M_right = +1.15
M_top = -0.10
M_bottom = +1.25
pose_name = ['Pitch', 'Yaw', 'Roll']


class FacePosDetector(object):
    # calculate the face angles based on DCNN frame caffe

    def __init__(self, deploy_path, model_path,  mean_path):
        self.vgg_point_net = None
        self.mean = None
        self.init_sys(deploy_path, model_path,  mean_path)


    def init_sys(self,deploy_path, model_path,  mean_path):
        # vgg_point_MODEL_FILE = '/library/vision/facedirection/model/deploy.prototxt'
        # vgg_point_PRETRAINED = '/library/vision/facedirection/model/68point_dlib_with_pose.caffemodel'
        # mean_filename='/library/vision/facedirection/model/VGG_mean.binaryproto'

        self.vgg_point_net=caffe.Net(deploy_path, model_path, caffe.TEST)
        # caffe.set_mode_cpu()
        caffe.set_mode_cpu()
        proto_data = open(mean_path, "rb").read()
        data_caffe = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
        self.mean = caffe.io.blobproto_to_array(data_caffe)[0]


    def predict(self, colorImage, bboxs, isVioldaJones = True):

        if isVioldaJones is True:
            # reshape the data from [x0 y0 w h] to [x0 y0 x1 y1]
            bboxs[:, 2:4] -= bboxs[:, 0:2]

        faceNum = bboxs.shape[0]
        faces = np.zeros((1,3,vgg_height,vgg_width))
        predictpoints = np.zeros((faceNum,pointNum*2))
        predictpose = np.zeros((faceNum,3))
        imgsize = np.zeros((2))
        imgsize[0] = colorImage.shape[0]-1
        imgsize[1] = colorImage.shape[1]-1

        TotalSize = np.zeros((faceNum,2))
        for i in range(0,faceNum):
            TotalSize[i] = imgsize
        for i in range(0,faceNum):
            bbox = bboxs[i]

            colorface = getRGBTestPart(bbox,M_left,M_right,M_top,M_bottom,colorImage,vgg_height,vgg_width)
            normalface = np.zeros(self.mean.shape)
            normalface[0] = colorface[:,:,0]
            normalface[1] = colorface[:,:,1]
            normalface[2] = colorface[:,:,2]
            normalface = normalface - self.mean
            faces[0] = normalface

            # landmark points


            blobName = '68point'
            data4DL = np.zeros([faces.shape[0],1,1,1])
            self.vgg_point_net.set_input_arrays(faces.astype(np.float32),data4DL.astype(np.float32))
            self.vgg_point_net.forward()
            predictpoints[i] = self.vgg_point_net.blobs[blobName].data[0]

            # pitch yaw roll angles

            blobName = 'poselayer'
            pose_prediction = self.vgg_point_net.blobs[blobName].data
            predictpose[i] = pose_prediction * 50


        predictpoints = predictpoints * vgg_height/2 + vgg_width/2
        level1Point = batchRecoverPart(predictpoints,bboxs,TotalSize,M_left,M_right,M_top,M_bottom,vgg_height,vgg_width)
        # show_image(colorImage, level1Point, bboxs, predictpose)

        return predictpose

def main():

    print " method called in face direction detect"

    vgg_point_MODEL_FILE = './model/deploy.prototxt'
    vgg_point_PRETRAINED = './model/68point_dlib_with_pose.caffemodel'
    mean_filename= './model/VGG_mean.binaryproto'

    detector = FacePosDetector(vgg_point_MODEL_FILE, vgg_point_PRETRAINED, mean_filename)

    while True:

        img = cv2.imread('34.jpg')
        # detect face use dlib face detector
        bboxs = detectFace(img)

        [x0,y0,x1,y1] = [bboxs[0][0],bboxs[0][2],bboxs[0][1],bboxs[0][3]]
        pos_str = str(x0) + " " + str(y0) + " " + str(x1) + " " + str(y1)

        if bboxs.shape[0] == 0:
            time.sleep(1)
            continue
        results = detector.predict(img, bboxs, False)
        try:

            fout = open('face_direction.txt', 'w')
            timer = time.time()
            for result in results:

                pitch_angle =  str(timer) + " "+ str(result[1]) + " " + pos_str
                print pitch_angle
                fout.write(pitch_angle.encode('utf-8') + '\n')
            fout.close()

        except ValueError:
            print "file in use!"
            time.sleep(0.1)
            continue

        time.sleep(1)


if __name__ == '__main__':
    main()
