# Author: Haotian Shi, Last Modified Date: 2016-02-17
from library.vision.Vision.FaceRecognitionAPI import  draw_face
from library.vision.facedirection.landmarkPredict import *
# import ewaybot_vision.Vision.FaceDetect as FD

# init caffe path
caffe_root = '/home/haotians/Documents/caffe/'
sys.path.insert(0, caffe_root + 'python')

import caffe
import dlib, math

vgg_height = 256
vgg_width = 256
M_left = -0.15
M_right = +1.15
M_top = -0.10
M_bottom = +1.25




class CNNDetection(object):
    def __init__(self, isGPU = False, model_path = None):
        # use cpu only
        self.mode_selection(isGPU)
        self.mean = None
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
        labels = []

        if path is None:
            print "emotion detect"
            deploy_path = 'VGG_S_rgb/deploy.prototxt'
            # model_path = 'VGG_S_rgb/model.caffemodel'
            model_path = 'VGG_S_rgb/EmotiW_VGG_S.caffemodel'#EmotiW_VGG_S
            mean_path = 'VGG_S_rgb/mean.binaryproto'
            labels = [ 'unhappy' , 'unhappy' , 'unhappy' , 'Happy'  , 'Neutral' ,  'unhappy' , 'Surprise']

        elif path == 'gender':
            deploy_path = 'age_gender_detect/deploy_gender.prototxt'
            model_path = 'age_gender_detect/gender_net.caffemodel'#EmotiW_VGG_S
            mean_path = 'age_gender_detect/mean.binaryproto'
            labels = [ 'Male' , 'Female', 'Fear' , 'Happy'  , 'Neutral' ,  'Sad' , 'Surprise']

        elif path == 'age':
            deploy_path = 'age_gender_detect/deploy_age.prototxt'
            model_path = 'age_gender_detect/age_net.caffemodel'#EmotiW_VGG_S
            mean_path = 'age_gender_detect/mean.binaryproto'
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

    def classification(self, target, class_num = None):

        if class_num is None:
            k = 5
        else:
            k = class_num

        # RGB format (0,1,2), BGR format (2,1,0), the reference model has channels in BGR order instead of RGB
        self.net.blobs['data'].data[...] = self.transformer.preprocess('data', target)
        out = self.net.forward()

        # sort top k predictions from softmax output
        result = out['prob'][0].flatten()

        top_k = result.argsort()[-1:-(1+k):-1]
        out_label = []
        out_confidence = []

        for i in range(k):
            label = self.labels[top_k[i]]
            confidence = result[top_k[i]]
            out_label.append(label)
            out_confidence.append(confidence)

        return out_label,out_confidence

    def detectFace(self,img):
        detector = dlib.get_frontal_face_detector()
        dets = detector(img,1)
        bboxs = np.zeros((len(dets),4))
        for i, d in enumerate(dets):
            bboxs[i,0] = d.left()
            bboxs[i,1] = d.right()
            bboxs[i,2] = d.top()
            bboxs[i,3] = d.bottom()
        return bboxs

    def classification_emotion(self, colorImage, bboxs, class_num = None, caffe_model_size = None):
        # bboxs = self.detectFace(colorImage)
        faceNum = bboxs.shape[0]

        if faceNum == 0:
            return None, None

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

        M_left = -0.15
        M_right = +1.15
        M_top = -0.15
        M_bottom = +1.25

        M_left = -0.05
        M_right = +1.05
        M_top = -0.05
        M_bottom = +1.05

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

            normalface = normalface - self.mean

            # faces[0] = normalface
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

    # emotion detect
    cnn_detector = CNNDetection()

    # age detect
    # cnn_detector = CNNDetection(False,'age')

    # gender detect
    # cnn_detector = CNNDetection(False,'gender')

    k = 0
    while True:
        timer1 = time.time()
        # Read image and convert to grayscale for processing
        ret, colorImage = cap.read()
        bboxs = detectFace(colorImage)

        # check the face size
        labels ,confidences= cnn_detector.classification_emotion(colorImage, bboxs, 2)

        timer2 =time.time()

        if labels is not None:
            for i in range(len(labels)):
                confidence = confidences[i][0]
                txt = labels[i][0]
                print "confidence and class and time consumption: ", confidence, txt, timer2-timer1

                if confidence >= 0.85:
                    draw_face(colorImage,
                              (int(bboxs[i,0]),int(bboxs[i,2]),int(bboxs[i,1]),int(bboxs[i,3])),
                              txt,None)

        cv2.imshow('Test Frame', colorImage)
        cv2.waitKey(10)
    cap.release()
    cv2.destroyAllWindows()

def emotion_test():
    import os


    DEMO_DIR = '.'

    categories = [ 'Angry' , 'Disgust' , 'Fear' , 'Happy'  , 'Neutral' ,  'Sad' , 'Surprise']

    # categories = [ 'Angry' , 'Sad' , 'Sad' , 'Happy'  , 'Neutral' ,  'Sad' , 'Surprise']

    cur_net_dir = 'VGG_S_rgb'

    mean_filename= os.path.join(DEMO_DIR,cur_net_dir,'mean.binaryproto')
    proto_data = open(mean_filename, "rb").read()
    a = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
    mean  = caffe.io.blobproto_to_array(a)[0]
    print mean

    net_pretrained = os.path.join(DEMO_DIR,cur_net_dir,'EmotiW_VGG_S.caffemodel')
    net_model_file = os.path.join(DEMO_DIR,cur_net_dir,'deploy.prototxt')

    VGG_S_Net = caffe.Classifier(net_model_file, net_pretrained,
                           mean=None,
                           channel_swap=None,
                           raw_scale=None,
                           image_dims=None)

    # VGG_S_Net = caffe.Net(net_model_file, net_model_file, caffe.TEST)

    transformer = caffe.io.Transformer({'data': VGG_S_Net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))
    transformer.set_mean('data', mean) # mean pixel

    name = 'test12.jpg'
    input_image = cv2.imread(name)
    # input_image = caffe.io.load_image(os.path.join(DEMO_DIR, cur_net_dir, name))
    # set net to batch size of 1
    VGG_S_Net.blobs['data'].reshape(1, 3, 256, 256)

    VGG_S_Net.blobs['data'].data[...] = transformer.preprocess('data', input_image)
    out = VGG_S_Net.forward()
    print out['prob'][0]

    print("Predicted class is #{}.".format(out['prob'][0]))

    print 'predicted category is {0}'.format(categories[out['prob'][0].argmax()])

    cv2.putText(input_image, categories[out['prob'][0].argmax()],(100,100), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 0), lineType=cv2.CV_AA)
    cv2.imshow('result',input_image)
    cv2.waitKey(0)

    name = "cnn_" + name
    cv2.imwrite(name, input_image)


def age_gender_test():

    age_list=['(0, 2)','(4, 6)','(8, 12)','(15, 20)','(25, 32)','(38, 43)','(48, 53)','(60, 100)']
    gender_list=['Male','Female']

    mean_filename= './age_gender_detect/mean.binaryproto'
    proto_data = open(mean_filename, "rb").read()
    a = caffe.io.caffe_pb2.BlobProto.FromString(proto_data)
    mean  = caffe.io.blobproto_to_array(a)[0]

    age_net_pretrained='./age_gender_detect/age_net.caffemodel'
    age_net_model_file='./age_gender_detect/deploy_age.prototxt'
    age_net = caffe.Net(age_net_model_file, age_net_pretrained, caffe.TEST)

    gender_net_pretrained='./age_gender_detect/gender_net.caffemodel'
    gender_net_model_file='./age_gender_detect/deploy_gender.prototxt'
    gender_net = caffe.Net(gender_net_model_file, gender_net_pretrained, caffe.TEST)

    transformer_g = caffe.io.Transformer({'data': gender_net.blobs['data'].data.shape})
    transformer_g.set_transpose('data', (2,0,1))
    transformer_g.set_mean('data', mean) # mean pixel

    transformer_a = caffe.io.Transformer({'data': age_net.blobs['data'].data.shape})
    transformer_a.set_transpose('data', (2,0,1))
    transformer_a.set_mean('data', mean) # mean pixel

    name = 'test6.jpg'
    input_image = cv2.imread(name)
    # input_image = caffe.io.load_image(os.path.join(DEMO_DIR, cur_net_dir, name))
    # set net to batch size of 1
    gender_net.blobs['data'].reshape(1, 3, 256, 256)
    gender_net.blobs['data'].data[...] = transformer_a.preprocess('data', input_image)

    age_net.blobs['data'].reshape(1, 3, 256, 256)
    age_net.blobs['data'].data[...] = transformer_a.preprocess('data', input_image)

    out_gender = gender_net.forward()
    out_age = age_net.forward()

    print "Prediction Age and confidence:", age_list[out_age['prob'][0].argmax()], out_age['prob'][0][out_age['prob'][0].argmax()]
    print "Prediction Gender and confidence:", gender_list[out_gender['prob'][0].argmax()], out_gender['prob'][0][out_gender['prob'][0].argmax()]

if __name__ == '__main__':
    test_cnn()
    # timer0 = time.time()
    # # detector = CNNDetection(False, 'models_cnn/VGG16')
    # detector = CNNDetection(False, None)
    # name = 'test19.jpg'
    # img = cv2.imread(name)
    # # print len(img[1279,:,0])
    # timer1 =time.time()
    # # detector.classification_vgg(img)
    # face_detector = dlib.get_frontal_face_detector()
    # box = detectFace(img)
    #
    # if box.shape[0]>0:
    #
    #     txt, confidence = detector.classification_emotion(img,box,2)
    #     print txt, confidence
    #     timer2 =time.time()
    #     print "time cost:", timer2 - timer1
    #     draw_face(img,
    #               (int(box[0,0]),int(box[0,2]),int(box[0,1]),int(box[0,3])),
    #               txt[0][0],None)
    #     # cv2.putText(img, txt[0][0], (100, 100), cv2.FONT_HERSHEY_PLAIN, 3.0, (0, 255, 0), lineType=cv2.CV_AA)
    #     cv2.imshow('test',img)
    #     cv2.waitKey(0)
    # else:
    #     print "can't find a face"




