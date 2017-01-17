import numpy as np
import matplotlib.pyplot as plt
import sys
import cv2
import time
import numpy

# Author: Haotian Shi, Last Modified Date: 2016-02-17
# init caffe path

caffe_root = '/home/haotians/Documents/caffe/'

# caffe_root = '/home/mini/github/caffe/'

sys.path.insert(0, caffe_root + 'python')

import caffe


class CNNDetection(object):
    def __init__(self, isGPU = False, model_path = None):
        # use cpu only
        self.mode_selection(isGPU)
        self.net, self.transformer ,self.labels = self.load_model(model_path)

    def mode_selection(self, isGPU):
        if isGPU:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()

    def load_model(self, path):
        # load trained model
        deploy_path = None
        model_path = None
        mean_path = None
        if path is None:
            deploy_path = 'models_cnn/NIN/deploy.prototxt'
            model_path = 'models_cnn/NIN/model.caffemodel'
            mean_path = 'models_cnn/NIN/ilsvrc_2012_mean.npy'
            labels_path = 'models_cnn/NIN/synset_words.txt'

        else:
            deploy_path = path + '/deploy.prototxt'
            model_path = path + '/model.caffemodel'
            mean_path = path + '/ilsvrc_2012_mean.npy'
            labels_path = path + '/synset_words.txt'

        net = caffe.Net(deploy_path, model_path, caffe.TEST)

        # set net to batch size of 1
        # net.blobs['data'].reshape(1, 3, 227, 227)
        net.blobs['data'].reshape(1, 3, 224, 224)
        # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        transformer.set_transpose('data', (2,0,1))
        # transformer.set_transpose('data', (2, 1, 0))
        transformer.set_mean('data', np.load(mean_path).mean(1).mean(1)) # mean pixel

        labels = np.loadtxt(path+'/translation.txt', str, delimiter='\t')

        return net, transformer, labels

    def classification(self, target):

        self.net.blobs['data'].data[...] = self.transformer.preprocess('data', target)
        out = self.net.forward()

        # sort top k predictions from softmax output
        k = 5
        result = out['prob'][0].flatten()
        # result = out['prob'][0].flatten()
        top_k = result.argsort()[-1:-(1+k):-1]
        out_label = []
        out_confidence = []

        for i in range(k):
            label = self.labels[top_k[i]]
            confidence = result[top_k[i]]
            out_label.append(label)
            out_confidence.append(confidence)

        return out_label,out_confidence

def test_cnn():

    # Create video capture object
    camera_num = 0
    cap = cv2.VideoCapture(camera_num)
    cap.set(3, 640)
    cap.set(4, 480)

    cnn_detector = CNNDetection(False, 'models_cnn/VGG_S')

    k = 0
    while cap.isOpened():
        k=k+1

        # Read image and convert to grayscale for processing
        ret, img = cap.read()
        # protect invalid reading
        # get faces
        if k%10 == 0:
            labels ,confidences= cnn_detector.classification(img)
            txt = labels[0]
            confidence = confidences[0]

            # get face length
            if confidence >= 0.3:
                print "label and confidence: ",txt,confidence
                cv2.putText(img, txt, (100, 100), cv2.FONT_HERSHEY_PLAIN, 2.0, (0, 255, 255), lineType=cv2.CV_AA)

            k = 0

        cv2.imshow('Test Frame', img)
        cv2.waitKey(5)

    cap.release()
    cv2.destroyAllWindows()

if __name__ == '__main__':
    test_cnn()
    timer0 = time.time()
    # detector = CNNDetection(False, 'models_cnn/VGG16')
    detector = CNNDetection(False, 'models_cnn/NIN')
    img = cv2.imread("test10.jpg")
    # print len(img[1279,:,0])
    timer1 =time.time()
    # detector.classification_vgg(img)
    detector.classification(img)
    timer2 =time.time()
    print "time cost:", timer2 - timer1
