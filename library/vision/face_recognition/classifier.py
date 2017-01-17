# Author: Yehang Liu, Last Modified Date: 2016-02-17

from distance import ChiSquareDistance, CosineDistance, EuclideanDistance
from util import asRowMatrix
import logging
import numpy as np
import operator as op

class AbstractClassifier(object):

    def compute(self,X,y):
        raise NotImplementedError("Every AbstractClassifier must implement the compute method.")
    
    def predict(self,X):
        raise NotImplementedError("Every AbstractClassifier must implement the predict method.")

    def update(self,X,y):
        raise NotImplementedError("This Classifier is cannot be updated.")

class NearestNeighbor(AbstractClassifier):
    """
    Implements a k-Nearest Neighbor Model with a generic distance metric.
    """
    def __init__(self, dist_metric=ChiSquareDistance(), k=1):
        AbstractClassifier.__init__(self)
        self.k = k
        self.dist_metric = dist_metric
        self.X = []
        self.y = np.array([], dtype=np.int32)

    def update(self, X, y):
        """
        Updates the classifier.
        """
        self.X.append(X)
        self.y = np.append(self.y, y)

    def compute(self, X, y):
        self.X = X
        self.y = np.asarray(y)
    
    def predict(self, q):
        """
        Predicts the k-nearest neighbor for a given query in q. 
        
        Args:
        
            q: The given query sample, which is an array.
            
        Returns:
        
            A list with the classifier output. In this framework it is
            assumed, that the predicted class is always returned as first
            element. Moreover, this class returns the distances for the 
            first k-Nearest Neighbors. 
            
            Example:
            
                [ 0, 
                   { 'labels'    : [ 0,      0,      1      ],
                     'distances' : [ 10.132, 10.341, 13.314 ]
                   }
                ]
            
            So if you want to perform a thresholding operation, you could 
            pick the distances in the second array of the generic classifier
            output.    
                    
        """
        distances = []
        for xi in self.X:
            xi = xi.reshape(-1,1)
            d = self.dist_metric(xi, q)
            distances.append(d)
        if len(distances) > len(self.y):
            raise Exception("More distances than classes. Is your distance metric correct?")
        distances = np.asarray(distances)
        # Get the indices in an ascending sort order:
        idx = np.argsort(distances)
        # Sort the labels and distances accordingly:
        sorted_y = self.y[idx]
        sorted_distances = distances[idx]
        # Take only the k first items:
        sorted_y = sorted_y[0:self.k]
        sorted_distances = sorted_distances[0:self.k]
        # Make a histogram of them:
        hist = dict((key,val) for key, val in enumerate(np.bincount(sorted_y)) if val)
        # And get the bin with the maximum frequency:
        predicted_label = max(hist.iteritems(), key=op.itemgetter(1))[0]
        # A classifier should output a list with the label as first item and
        # generic data behind. The k-nearest neighbor classifier outputs the 
        # distance of the k first items. So imagine you have a 1-NN and you
        # want to perform a threshold against it, you should take the first
        # item
        # return [predicted_label, { 'labels' : sorted_y, 'distances' : sorted_distances }]
        return predicted_label, sorted_distances
        
    def __repr__(self):
        return "NearestNeighbor (k=%s, dist_metric=%s)" % (self.k, repr(self.dist_metric))