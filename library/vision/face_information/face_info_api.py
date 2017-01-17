# Author: Haotian Shi, Last Modified Date: 2016-02-17
from library.vision.facedirection.landmarkPredict import *
# init caffe path
# caffe_root = '/home/haotians/Documents/caffe/'
caffe_root = '/home/yan-eway/github/caffe/'
sys.path.insert(0, caffe_root + 'python')

import caffe

vgg_height = 256
vgg_width = 256

class DeepFaceInfo(object):
    def __init__(self, isGPU = False, type = None, model_path = None):
        # use cpu only
        self.mode_selection(isGPU)
        self.mean = None
        self.net, self.transformer ,self.labels = self.load_model(type, model_path)

    def mode_selection(self, isGPU):
        if isGPU:
            caffe.set_mode_gpu()
        else:
            caffe.set_mode_cpu()

    def load_model(self, type, path):
        # load trained model
        deploy_path = None
        model_path = None
        mean_path = None
        labels = []

        if type is 'emotion':
            deploy_path = path + 'VGG_S_rgb/deploy.prototxt'
            model_path = path + 'VGG_S_rgb/EmotiW_VGG_S.caffemodel'#EmotiW_VGG_S
            mean_path = path + 'VGG_S_rgb/mean.binaryproto'

            labels = [ 'unhappy' , 'unhappy' , 'unhappy' , 'Happy'  , 'Neutral' ,  'unhappy' , 'Surprise']

        elif type == 'gender':
            deploy_path = path + 'age_gender_detect/deploy_gender.prototxt'
            model_path = path + 'age_gender_detect/gender_net.caffemodel'#EmotiW_VGG_S
            mean_path = path + 'age_gender_detect/mean.binaryproto'
            labels = [ 'Male' , 'Female']

        elif type == 'age':
            deploy_path = path + 'age_gender_detect/deploy_age.prototxt'
            model_path = path +  'age_gender_detect/age_net.caffemodel'#EmotiW_VGG_S
            mean_path = path + 'age_gender_detect/mean.binaryproto'
            labels = ['(0, 2)','(4, 6)','(8, 12)','(15, 20)','(25, 32)','(38, 43)','(48, 53)','(60, 100)']

        # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        proto_data = open(mean_path, "rb").read()
        data = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
        mean  = caffe.io.blobproto_to_array(data)[0]
        self.mean = mean
        net = caffe.Net(deploy_path, model_path, caffe.TEST)
        # set net to batch size of 1
        net.blobs['data'].reshape(1, 3, 256, 256)
        # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
        transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
        # caffe expected data in channel-height-width(2,0,1) format, not height-width-channel(0,1,2) format
        transformer.set_transpose('data', (2,1,0))
        transformer.set_mean('data', mean) # mean pixel
        return net, transformer, labels

    def face_info_extract(self, colorImage, bboxs = None, class_num = None, caffe_model_size = None):
        # if bboxs is None, assume that only raw image is passed to the function
        # and this method will preform face detect by itself
        if bboxs is None:
            bboxs = detectFace(colorImage)

        faceNum = bboxs.shape[0]
        # if no image is detected, return None and None instead of going deep for CNN.forward
        if faceNum == 0:
            return None, None

        # default face size is 256
        if caffe_model_size is None:
            vgg_height = vgg_width = 256
        else:
            vgg_height = vgg_width = caffe_model_size

        # face holder
        faces = np.zeros((1,3,vgg_height,vgg_width))

        # size
        imgsize = np.zeros((2))
        imgsize[0] = colorImage.shape[0]-1
        imgsize[1] = colorImage.shape[1]-1

        TotalSize = np.zeros((faceNum,2))
        TotalSize[0] = imgsize

        # output values
        face_labels = []
        face_confidences = []

        M_left = -0.1
        M_right = +1.1
        M_top = -0.25
        M_bottom = +1.2

        # loop over all the faces:
        for i in range(faceNum):

            # get face box
            bbox = bboxs[i]
            # reshape the box into caffe model requirement
            colorface = getRGBTestPart(bbox, M_left, M_right, M_top ,M_bottom, colorImage, vgg_height, vgg_width)
            normalface = np.zeros(self.mean.shape)

            normalface[0] = colorface[:,:,0]
            normalface[1] = colorface[:,:,1]
            normalface[2] = colorface[:,:,2]

            # make normal face  y extract mean value information
            # todo: this must be modified for better performance
            normalface = normalface - self.mean

            # load face and run the network
            self.net.blobs['data'].data[...] = normalface
            out = self.net.forward()
            # sort top k predictions from softmax output
            result = out['prob'][0].flatten()

            if class_num is None:
                k = 5
            else:
                k = class_num
            # get result
            top_k = result.argsort()[-1:-(1+k):-1]
            out_label = []
            out_confidence = []

            for i in range(k):
                label = self.labels[top_k[i]]
                confidence = result[top_k[i]]
                out_label.append(label)
                out_confidence.append(confidence)

            face_labels.append(out_label)
            face_confidences.append(out_confidence)

        return face_labels, face_confidences

def test_cnn():
    reshape_size =15

    # Create video capture object
    camera_num = 0
    cap = cv2.VideoCapture(camera_num)
    cap.set(3, 640)
    cap.set(4, 480)

    path = '/home/haotians/Documents/Github/Vision/library/vision/face_information/'

    # emotion detect
    cnn_detector = DeepFaceInfo(False,'emotion',path)

    '/home/haotians/Documents/Github/Vision/library/vision/face_information/VGG_S_rgb'

    # age detect
    # cnn_detector = DeepFaceInfo(False,'age',path)

    # gender detect
    # cnn_detector = DeepFaceInfo(False,'gender',path)

    k = 0
    while True:
        timer1 = time.time()
        # Read image and convert to grayscale for processing
        ret, colorImage = cap.read()

        if k % 10 == 0:
            bboxs = detectFace(colorImage)

            # check the face size
            labels ,confidences= cnn_detector.face_info_extract(colorImage, bboxs, 2)

            timer2 =time.time()

            if labels is not None:
                for i in range(len(labels)):
                    confidence = confidences[i][0]
                    txt = labels[i][0]
                    if confidence > 0.9:
                        print "confidence and class and time consumption: ", confidence, txt, timer2-timer1

        cv2.imshow('Test Frame', colorImage)
        cv2.waitKey(10)
    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    test_cnn()


