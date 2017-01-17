# Author: Yehang Liu, Last Modified Date: 2016-02-17

import os
import sys
import numpy as np

import cv2

from library.vision.face_recognition.feature import SpatialHistogram, LGBP_small, LGBP_single, LPQ
from library.vision.face_recognition.distance import ChiSquareDistance, CosineDistance, EuclideanDistance
from library.vision.face_recognition.classifier import NearestNeighbor
from library.vision.face_recognition.model import ExtendedPredictableModel
from library.vision.face_recognition.preprocessing import TanTriggsPreprocessing
from library.vision.face_recognition.operators import ChainOperator
from library.vision.face_recognition.serialization import load_model, save_model


class FaceRecognizer(object):

    def __init__(self,path=None):
        self.face_model = None
        path = os.getcwd()
        #path = os.path.dirname(path)
        #path = path + '/face_recognition/trained_face_model.pkl'
        path = path + '/library/vision/face_recognition/trained_face_model.pkl'
        self.path = path
        print path
        if path is None:
            self.face_model = load_model("../face_recognition/trained_face_model.pkl")
        else:
            self.face_model = load_model(self.path)



    def face_recognition(self, gray, faces, mode=True):

        face_name = []
        prediction_list = []
         # KNN threshold fisherface(): 800, SpatialHistogram: 1.7, PCA: bad features, LDA: bad features
        threshold = 32
        faces_length = len(faces)
        # loop over all the faces
        for i in range(faces_length):

            x0, y0, x1, y1 = faces[i]
            # get the face
            face = gray[y0:y1, x0:x1]
            # reshape the face
            face_reshape = cv2.resize(face, (92,112), interpolation = cv2.INTER_CUBIC)
            face_reshape = self.contrast_stretch2(face_reshape)
            # cv2.imshow('processed', face_reshape)
            # cv2.waitKey(10)
            # Get a prediction from the model:
            prediction, nn_distance = self.face_model.predict(face_reshape)
            name = self.face_model.subject_names[prediction]
            if nn_distance > threshold:
                name = "Not in the data base"
            print nn_distance
            # print name
            face_name.append(name)
            # prediction_list.append(prediction)
        # print "result: ", face_name
        return face_name

    def read_images(self, path, image_size=None):
        # Args:
        #     path: Path to a folder with subfolders representing the subjects (persons).
        #     sz: A tuple with the size Resizes
        # Returns:
        #     A list [X, y, folder_names]
        #     X: The images, which is a Python list of numpy arrays.
        #     y: The corresponding labels (the unique number of the subject, person) in a Python list.
        #     folder_names: The names of the folder, so you can display it in a prediction.

        c = 0
        X = []
        y = []
        folder_names = []
        for dirname, dirnames, filenames in os.walk(path):
            for subdirname in dirnames:
                folder_names.append(subdirname)
                subject_path = os.path.join(dirname, subdirname)
                for filename in os.listdir(subject_path):
                    try:
                        im = cv2.imread(os.path.join(subject_path, filename), cv2.IMREAD_GRAYSCALE)
                        im = cv2.equalizeHist(im)
                        # resize to given size (if given)
                        if (image_size is not None):
                            im = cv2.resize(im, image_size)
                        X.append(np.asarray(im, dtype=np.uint8))
                        y.append(c)
                    except IOError, (errno, strerror):
                        print "I/O error({0}): {1}".format(errno, strerror)
                    except:
                        print "Unexpected error:", sys.exc_info()[0]
                        raise
                c = c+1
        return [X, y, folder_names]


    def train_face_model(self, path, image_size):
        [images, labels, subject_names] = self.read_images(path, None)
        # Zip us a {label, name} dict from the given data:
        list_of_labels = list(xrange(max(labels)+1))
        subject_dictionary = dict(zip(list_of_labels, subject_names))
        # Get the model we want to compute:

        model = self.get_model(image_size = (92, 112), subject_names=subject_dictionary,
                          feature = ChainOperator(TanTriggsPreprocessing(), SpatialHistogram()))
        model.compute(images, labels)

        # save model to local directory
        if self.path is None:
            save_model("face_recognition/trained_face_model.pkl", model)
        else:
            save_model(self.path,model)


    # define model
    def get_model(self,image_size, subject_names, feature = None, classifier = None):
        # Define the SpatialHistogram Method as Feature Extraction method:
        if feature is None:
            # feature = Fisherfaces()
            feature = SpatialHistogram
            # feature = PCA()
            # feature = LDA()
        # Define a 1-NN classifier with Euclidean Distance:
        if classifier is None:
            classifier = NearestNeighbor(dist_metric=ChiSquareDistance(), k=1)
        # Return the model as the combination:
        return ExtendedPredictableModel(feature=feature, classifier=classifier,
                                        image_size=image_size, subject_names=subject_names)

    def contrast_stretch2(self, image):
        result = cv2.equalizeHist(image)
        return result
        lut = np.zeros(256, dtype = image.dtype )

        hist,bins = np.histogram(image.flatten(),256,[0,256])
        cdf = hist.cumsum()
        cdf_m = np.ma.masked_equal(cdf,0)
        cdf_m = (cdf_m - cdf_m.min())*255/(cdf_m.max()-cdf_m.min())
        cdf = np.ma.filled(cdf_m,0).astype('uint8')

        # result2 = cdf[image]
        result = cv2.LUT(image, cdf)
        return result

    def contrast_stretch(self, image):
        row, col = np.shape(image)
        g_log = np.zeros([row, col], dtype=np.float32)
        g = np.zeros([row, col], dtype=np.float32)
        prob = np.zeros([1, 256], dtype=np.float32)
        cdf = np.zeros([1, 256], dtype=np.float32)
        g_out = np.zeros([row, col], dtype=np.uint8)
        temp = 0.0
        for i in range(row):
            for j in range(col):
                temp = float(image[i, j])
                g_log[i, j] = 255 * np.power((temp / 255), 0.3)
                prob[0, round(g_log[i, j])] += 1
        prob /= (row * col)
        cdf[0, 0] = prob[0, 0]
        for i in range(1, 256):
            cdf[0, i] = cdf[0, i - 1] + prob[0, i]
        for i in range(256):
            cdf[0, i] = cdf[0, i] * i
        for i in range(row):
            for j in range(col):
                g[i, j] = cdf[0, round(g_log[i, j])]
        min_g = np.min(g)
        max_g = np.max(g)
        # g_out = (g - min_g) / (max_g - min_g) * 255
        for i in range(row):
            for j in range(col):
                g_out[i, j] = int((g[i, j] - min_g) / (max_g - min_g) * 255)
        return g_out

if __name__ == '__main__':
    fr = FaceRecognizer()
    fr.train_face_model('../face_recognition/', [92,112])
    # im = cv2.imread('../face_recognition/1.png', 0)
    # im2 = cv2.equalizeHist(im)
    # cv2.imshow('test', im2)
    # cv2.waitKey(30000)
