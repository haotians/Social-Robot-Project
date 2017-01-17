# Author: Yehang Liu, Last Modified Date: 2016-02-17

import os
import numpy as np
import sys

import cv2

from library.vision.face_recognition.feature import SpatialHistogram
from library.vision.face_recognition.distance import EuclideanDistance
from library.vision.face_recognition.classifier import NearestNeighbor
from library.vision.face_recognition.model import ExtendedPredictableModel
from library.vision.face_recognition.preprocessing import TanTriggsPreprocessing
from library.vision.face_recognition.operators import ChainOperator
from library.vision.face_recognition.serialization import save_model


def face_recognition(gray, faces, face_model):

    face_name = []
     # KNN threshold fisherface(): 800, SpatialHistogram: 1.7, PCA: bad features, LDA: bad features
    threshold = 1.75
    faces_length = len(faces)
    # loop over all the faces
    for i in range(faces_length):

        x0, y0, x1, y1 = faces[i]
        # get the face
        face = gray[y0:y1, x0:x1]
        # reshape the face
        face_reshape = cv2.resize(face, face_model.image_size, interpolation = cv2.INTER_CUBIC)
        # Get a prediction from the model:
        prediction, nn_distance= face_model.predict(face_reshape)
        # Draw the predicted name (folder name...):
        name = face_model.subject_names[prediction]
        # print nn_distance
        # if the distance is larger than threshold, consider it as a false match
        if nn_distance > threshold:
            name = "Not in the data base"
        #
        # cv2.waitKey(10)
        face_name.append(name)
    # print "result: ", face_name
    return face_name


def read_images(path, image_size=None):
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


def train_face_model(path, image_size):
    print "Loading dataset..."
    [images, labels, subject_names] = read_images(path, None)
    print labels
    print subject_names
    # Zip us a {label, name} dict from the given data:
    list_of_labels = list(xrange(max(labels)+1))
    subject_dictionary = dict(zip(list_of_labels, subject_names))
    # Get the model we want to compute:
    model = get_model(image_size = image_size, subject_names=subject_dictionary,
                      feature = ChainOperator(TanTriggsPreprocessing(), SpatialHistogram()))
    print "Computing the model..."
    model.compute(images, labels)
    # save model to local directory
    save_model("Vision/trained_face_model.pkl", model)
    print "face model saved"


def get_training_data(Name):
    # face size
    face_size = (92, 112)
    # Create video capture object
    camera_num = 1
    cap = cv2.VideoCapture(camera_num)
    cap.set(3, 640)
    cap.set(4, 480)

    cascade_model = select_trained_cascade_model(None)

    # create folder
    path = "face_recognition/"+Name

    print path

    if not os.path.exists(path):
        os.makedirs(path)

    k = 0

    while cap.isOpened():

        # Read image and convert to grayscale for processing
        ret, img = cap.read()
        # protect invalid reading
        if not ret:
            continue
        # get faces
        faces, gray = face_cascade_detect(img, cascade_model)
        # get face length
        faces_length = len(faces)
        if faces_length < 1 or faces_length > 1:
            continue
        # sampling increment
        k = k + 1
        # sampling gap
        if k % 10 == 0:
            print str(k/5)
            # face location
            x0, y0, x1, y1 = faces[0]
            # get the face img
            face = gray[y0:y1, x0:x1]
            # reshape the face
            face_reshape = cv2.resize(face, face_size, interpolation = cv2.INTER_CUBIC)
            cv2.imwrite(path+"/"+str(k/5)+".png", face_reshape)

        cv2.imshow('Test Frame', img)
        cv2.waitKey(5)

        if k/10 > 15:
            # samples is enough
            print "Sampling ends"
            break

    cap.release()
    cv2.destroyAllWindows()


def draw_face(dst, (x0, y0, x1, y1), txt, distance = None):
    # draw name
    if txt is not None:
        cv2.putText(dst, txt, (x0-20, y0-20), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 0), lineType=cv2.CV_AA)
    # draw distance
    if distance is not None:
        cv2.putText(dst, distance, (x0-20, y0), cv2.FONT_HERSHEY_PLAIN, 2.0, (255, 255, 0), lineType=cv2.CV_AA)
    # Draw the face area in image:
    cv2.rectangle(dst, (x0, y0),(x1,y1), (0,255,0), 2)
    cv2.waitKey(10)


# define model
def get_model(image_size, subject_names, feature = None, classifier = None):
    # Define the SpatialHistogram Method as Feature Extraction method:
    if feature is None:
        # feature = Fisherfaces()
        feature = SpatialHistogram
        # feature = PCA()
        # feature = LDA()
    # Define a 1-NN classifier with Euclidean Distance:
    if classifier is None:
        classifier = NearestNeighbor(dist_metric=EuclideanDistance(), k=1)
    # Return the model as the combination:
    return ExtendedPredictableModel(feature=feature, classifier=classifier,
                                    image_size=image_size, subject_names=subject_names)


def select_trained_cascade_model(path=None):
    if path is None:
        path = "Vision/cascade_models/haarcascade_frontalface_alt2.xml"
        # path = "cascade_models/haarcascade_frontalface_alt2.xml" # local use
        # path = "/usr/local/share/OpenCV/cascade_models/haarcascade_frontalface_alt2.xml"
    cascade_model = cv2.CascadeClassifier(path)
    return cascade_model


def face_cascade_detect(img, cascade_model):
    # opencv based viola jones face detector
    # not super good
    gray = None
    # convert to gray scale
    if np.ndim(img) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # as assume single channel data is grayscaled image
    elif np.ndim(img) == 1:
        pass
        gray = img
    # normalizes the brightness and increases the contrast of the image
    gray_normal = cv2.equalizeHist(gray)
    # get faces
    faces = cascade_model.detectMultiScale(gray_normal, scaleFactor=1.3,
                                           minNeighbors=4, minSize=(28, 28),
                                           flags=cv2.cv.CV_HAAR_FEATURE_MAX)
    # avoid null pointer
    if len(faces) > 0:
        # reshape the data from [x0 y0 w h] to [x0 y0 x1 y1]
        faces[:, 2:4] += faces[:, 0:2]
    return faces, gray