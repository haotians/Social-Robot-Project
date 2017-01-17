# Author: Yehang Liu, Last Modified Date: 2016-02-17

import numpy as np
import cv2, scipy

class AbstractFeature(object):

    def compute(self,X,y):
        raise NotImplementedError("Every AbstractFeature must implement the compute method.")
    
    def extract(self,X):
        raise NotImplementedError("Every AbstractFeature must implement the extract method.")
        
    def save(self):
        raise NotImplementedError("Not implemented yet (TODO).")
    
    def load(self):
        raise NotImplementedError("Not implemented yet (TODO).")
        
    def __repr__(self):
        return "AbstractFeature"

class Identity(AbstractFeature):
    """
    Simplest AbstractFeature you could imagine. It only forwards the data and does not operate on it, 
    probably useful for learning a Support Vector Machine on raw data for example!
    """
    def __init__(self):
        AbstractFeature.__init__(self)
        
    def compute(self,X,y):
        return X
    
    def extract(self,X):
        return X
    
    def __repr__(self):
        return "Identity"


from util import asColumnMatrix
# from operators import ChainOperator, CombineOperator
        
class PCA(AbstractFeature):
    def __init__(self, num_components=0):
        AbstractFeature.__init__(self)
        self._num_components = num_components
        
    def compute(self,X,y):
        # build the column matrix
        XC = asColumnMatrix(X)
        y = np.asarray(y)
        # set a valid number of components
        if self._num_components <= 0 or (self._num_components > XC.shape[1]-1):
            self._num_components = XC.shape[1]-1
        # center dataset
        self._mean = XC.mean(axis=1).reshape(-1,1)
        XC = XC - self._mean
        # perform an economy size decomposition (may still allocate too much memory for computation)
        self._eigenvectors, self._eigenvalues, variances = np.linalg.svd(XC, full_matrices=False)
        # sort eigenvectors by eigenvalues in descending order
        idx = np.argsort(-self._eigenvalues)
        self._eigenvalues, self._eigenvectors = self._eigenvalues[idx], self._eigenvectors[:,idx]
        # use only num_components
        self._eigenvectors = self._eigenvectors[0:,0:self._num_components].copy()
        self._eigenvalues = self._eigenvalues[0:self._num_components].copy()
        # finally turn singular values into eigenvalues 
        self._eigenvalues = np.power(self._eigenvalues,2) / XC.shape[1]
        # get the features from the given data
        features = []
        for x in X:
            xp = self.project(x.reshape(-1,1))
            features.append(xp)
        return features
    
    def extract(self,X):
        X = np.asarray(X).reshape(-1,1)
        return self.project(X)
        
    def project(self, X):
        X = X - self._mean
        return np.dot(self._eigenvectors.T, X)

    def reconstruct(self, X):
        X = np.dot(self._eigenvectors, X)
        return X + self._mean

    @property
    def num_components(self):
        return self._num_components

    @property
    def eigenvalues(self):
        return self._eigenvalues
        
    @property
    def eigenvectors(self):
        return self._eigenvectors

    @property
    def mean(self):
        return self._mean
        
    def __repr__(self):
        return "PCA (num_components=%d)" % (self._num_components)
        
class LDA(AbstractFeature):

    def __init__(self, num_components=0):
        AbstractFeature.__init__(self)
        self._num_components = num_components

    def compute(self, X, y):
        # build the column matrix
        XC = asColumnMatrix(X)
        y = np.asarray(y)
        # calculate dimensions
        d = XC.shape[0]
        c = len(np.unique(y))        
        # set a valid number of components
        if self._num_components <= 0:
            self._num_components = c-1
        elif self._num_components > (c-1):
            self._num_components = c-1
        # calculate total mean
        meanTotal = XC.mean(axis=1).reshape(-1,1)
        # calculate the within and between scatter matrices
        Sw = np.zeros((d, d), dtype=np.float32)
        Sb = np.zeros((d, d), dtype=np.float32)
        for i in range(0,c):
            Xi = XC[:,np.where(y==i)[0]]
            meanClass = np.mean(Xi, axis = 1).reshape(-1,1)
            Sw = Sw + np.dot((Xi-meanClass), (Xi-meanClass).T)
            Sb = Sb + Xi.shape[1] * np.dot((meanClass - meanTotal), (meanClass - meanTotal).T)
        # solve eigenvalue problem for a general matrix
        self._eigenvalues, self._eigenvectors = np.linalg.eig(np.linalg.inv(Sw)*Sb)
        # sort eigenvectors by their eigenvalue in descending order
        idx = np.argsort(-self._eigenvalues.real)
        self._eigenvalues, self._eigenvectors = self._eigenvalues[idx], self._eigenvectors[:,idx]
        # only store (c-1) non-zero eigenvalues
        self._eigenvalues = np.array(self._eigenvalues[0:self._num_components].real, dtype=np.float32, copy=True)
        self._eigenvectors = np.matrix(self._eigenvectors[0:,0:self._num_components].real, dtype=np.float32, copy=True)
        # get the features from the given data
        features = []
        for x in X:
            xp = self.project(x.reshape(-1,1))
            features.append(xp)
        return features
        
    def project(self, X):
        return np.dot(self._eigenvectors.T, X)

    def reconstruct(self, X):
        return np.dot(self._eigenvectors, X)

    @property
    def num_components(self):
        return self._num_components

    @property
    def eigenvectors(self):
        return self._eigenvectors
    
    @property
    def eigenvalues(self):
        return self._eigenvalues
    
    def __repr__(self):
        return "LDA (num_components=%d)" % (self._num_components)
        
class Fisherfaces(AbstractFeature):

    def __init__(self, num_components=0):
        AbstractFeature.__init__(self)
        self._num_components = num_components
    
    def compute(self, X, y):
        # turn into numpy representation
        Xc = asColumnMatrix(X)
        y = np.asarray(y)
        # gather some statistics about the dataset
        n = len(y)
        c = len(np.unique(y))
        # define features to be extracted
        pca = PCA(num_components = (n-c))
        lda = LDA(num_components = self._num_components)
        # fisherfaces are a chained feature of PCA followed by LDA
        model = ChainOperator(pca,lda)
        # computing the chained model then calculates both decompositions
        model.compute(X,y)
        # store eigenvalues and number of components used
        self._eigenvalues = lda.eigenvalues
        self._num_components = lda.num_components
        # compute the new eigenspace as pca.eigenvectors*lda.eigenvectors
        self._eigenvectors = np.dot(pca.eigenvectors,lda.eigenvectors)
        # finally compute the features (these are the Fisherfaces)
        features = []
        for x in X:
            xp = self.project(x.reshape(-1,1))
            features.append(xp)
        return features

    def extract(self,X):
        X = np.asarray(X).reshape(-1,1)
        return self.project(X)

    def project(self, X):
        return np.dot(self._eigenvectors.T, X)
    
    def reconstruct(self, X):
        return np.dot(self._eigenvectors, X)

    @property
    def num_components(self):
        return self._num_components
        
    @property
    def eigenvalues(self):
        return self._eigenvalues
    
    @property
    def eigenvectors(self):
        return self._eigenvectors

    def __repr__(self):
        return "Fisherfaces (num_components=%s)" % (self.num_components)

from lbp import LocalDescriptor, ExtendedLBP, OriginalLBP, LPQ, VarLBP

class SpatialHistogram(AbstractFeature):
    def __init__(self, lbp_operator=ExtendedLBP(), sz = (8,8)):
        AbstractFeature.__init__(self)
        if not isinstance(lbp_operator, LocalDescriptor):
            raise TypeError("Only an operator of type facerec.lbp.LocalDescriptor is a valid lbp_operator.")
        self.lbp_operator = lbp_operator
        self.sz = sz
        
    def compute(self,X,y):
        features = []
        for x in X:
            x = np.asarray(x)
            h = self.spatially_enhanced_histogram(x)
            features.append(h)
        return features
    
    def extract(self,X):
        X = np.asarray(X)
        return self.spatially_enhanced_histogram(X)

    def spatially_enhanced_histogram(self, X):
        # calculate the LBP image
        L = self.lbp_operator(X)
        # calculate the grid geometry
        lbp_height, lbp_width = L.shape
        grid_rows, grid_cols = self.sz
        py = int(np.floor(lbp_height/grid_rows))
        px = int(np.floor(lbp_width/grid_cols))
        E = []
        for row in range(0,grid_rows):
            for col in range(0,grid_cols):
                C = L[row*py:(row+1)*py,col*px:(col+1)*px]
                H = np.histogram(C, bins=2**self.lbp_operator.neighbors, range=(0, 2**self.lbp_operator.neighbors), normed=True)[0]
                # probably useful to apply a mapping?
                E.extend(H)
        return np.asarray(E)
    
    def __repr__(self):
        return "SpatialHistogram (operator=%s, grid=%s)" % (repr(self.lbp_operator), str(self.sz))

class LGBP(AbstractFeature):
    def __init__(self, scales=3, orients=5):
        AbstractFeature.__init__(self)
        self.scales = scales
        self.orients = orients
        self.height = 112
        self.width = 96
        self.block_size = 16
        self.lbp = OriginalLBP()

    def Gabor_kernel_single(self, orient, scale):
        k_max = np.pi / 2
        delta = 7 * np.pi / 4
        f = np.sqrt(2)
        theta_u = np.pi * orient / self.orients
        k_v = k_max / (f ** scale)
        k_uv = [k_v * np.cos(theta_u), k_v * np.sin(theta_u)]
        filter_single = np.zeros([self.height, self.width], np.complex)

        for x in range(self.height):
            for y in range(self.width):
                coefficient = (k_v ** 2) / (delta ** 2) * \
                    np.exp(-np.square(k_v) * (np.square(x) + np.square(y)) / (2 * np.square(delta)))
                kernel = np.exp(1j * (x * k_uv[0] + y * k_uv[1])) - np.exp(- np.square(delta) * 2)
                # imaginary = kernel.imag * coefficient
                # real = kernel.real * coefficient
                # filter_single
                # filter_single[x][y] = np.sqrt(imaginary ** 2 + real ** 2)
                filter_single[x][y] = kernel * coefficient

        return filter_single

    def Gabor_kernel_all(self):
        Gabor_filters = []
        for i in range(self.orients):
            for k in range(self.scales):
                Gabor_filters.append(self.Gabor_kernel_single(i, k))
        return Gabor_filters

    def image_filtering(self, image):
        filters = self.Gabor_kernel_all()
        filtered_images = []
        filtered_image = []
        image = np.fft.fft2(image)
        for i in range(self.orients * self.scales):
            # filtered_image.append(np.convolve(image, filters[i],'same'))
            # filtered_image = (cv2.filter2D(image,-1,filters[i]))
            filtered_image = np.abs(np.fft.ifft2(image * np.fft.fft2(filters[i])))
            # filtered_image = np.abs(filtered_image)
            filtered_image = self.original_lbp(filtered_image)
            filtered_images.append(filtered_image)
            filtered_image = []
        return filtered_images

    def original_lbp(self, filtered_image):
        # block = np.zeros(self.block_size, self.block_size)
        features_lbp = np.zeros([self.height, self.width])
        feature_temp = 0

        appened_image = self.image_append(filtered_image)

        for i in range(1, self.height+1):
            for j in range(1, self.width+1):
                center_value = appened_image[i][j]
                feature_temp = (center_value < appened_image[i-1][j-1]) * 1 + (center_value < appened_image[i-1][j]) * 2 + \
                               (center_value < appened_image[i-1][j+1]) * 4 + (center_value < appened_image[i][j-1]) * 8 + \
                               (center_value < appened_image[i+1][j+1]) * 16 + (center_value < appened_image[i+1][j]) * 32 + \
                               (center_value < appened_image[i+1][j-1]) * 64 + (center_value < appened_image[i][j-1]) * 128
                features_lbp[i-1][j-1] = feature_temp

        block = np.zeros([self.block_size, self.block_size])
        hist = []
        for i in range(self.height / self.block_size):
            for j in range(self.width / self.block_size):
                block = features_lbp[i*self.block_size:(i+1)*self.block_size,j*self.block_size:(j+1)*self.block_size]
                # hist_temp, bins = np.histogram((block.flatten(), 256, [0,256]))
                # hist_temp = cv2.calcHist([block], [0], None, [256], [0.0,255.0])
                hist_temp = self.histogram(block)
                hist.append(hist_temp)
        return hist

    def LGBP_feature(self, filtered_images):
        features = self.image_filtering(filtered_images)
        total = self.orients * self.scales * self.height * self.width / \
                np.square(self.block_size) * 256
        # row, col = np.shape(features)
        features_final = np.reshape(features,[total,1])

        return features_final

    def image_append(self, image):
        image_new = np.zeros([self.height+2, self.width+2], int)
        image_new[0][0] = image[self.height-1][self.width-1]
        image_new[0][self.width+1] = image[self.height-1][0]
        image_new[self.height+1][0] = image[0][self.width-1]
        image_new[self.height+1][self.width-1] = image[0][0]
        image_new[1:self.height+1,1:self.width+1] = image
        image_new[0,1:self.width+1] = image[self.height-1]
        image_new[self.height+1,1:self.width+1] = image[0]
        image_new[1:self.height+1,0] = image[0:self.height,self.width-1]
        image_new[1:self.height+1,self.width+1] = image[0:self.height,0]
        # cv2.imwrite('test.png', image_new)
        # cv2.imshow('test', image_new)
        # cv2.waitKey(3000)
        return image_new

    def histogram(self, image):
        hist = np.zeros([1,256],int)
        for i in range(self.block_size):
            for j in range(self.block_size):
                hist[0][int(image[i][j])] += 1

        return hist

    def extract(self,X):
        X = np.asarray(X)
        return self.LGBP_feature(X)

    def compute(self,X,y):
        features = []
        for x in X:
            x = np.asarray(x)
            h = self.LGBP_feature(x)
            features.append(h)
        # features = self.LGBP_feature(X)
        return features

class LGBP_small(AbstractFeature):
    def __init__(self, scales=1, orients=3):
        AbstractFeature.__init__(self)
        self.scales = scales
        self.orients = orients
        self.block_size = 16
        self.step = 11
        self.lbp = LPQ()

    def gabor_single(self, x, y, f0, theta):
        r = 1
        g = 1
        x1 = x * np.cos(theta) + y * np.sin(theta)
        y1 = - x * np.sin(theta) + y * np.cos(theta)
        gabor = f0 ** 2 / (np.pi * r * g) * np.exp(-(np.power(f0, 2) * np.power(x1, 2) / np.power(r, 2) +
                                                     np.power(f0, 2) * np.power(y1, 2) / np.power(g, 2))) * \
                                                     np.exp(1j * 2 * np.pi * f0 * x1)
        return gabor

    def gabor_filter(self, image):
        # row, col = np.shape(image)
        scales = np.linspace(-5, 5, self.step)
        theta_range = np.linspace(0, np.pi, self.orients)
        # print theta_range
        # theta_range = [2 * np.pi / 3]
        f0 = 0.2
        # counter = 0
        filter_gabor = np.zeros([self.step, self.step], dtype=np.complex)
        # result_temp_real = np.zeros([row, col], dtype=np.float)
        # result_temp_imag = np.zeros([row, col], dtype=np.float)
        filtered_images = []
        # filtered_image = np.zeros([row, col], dtype=np.complex)
        image = np.asarray(image, dtype=np.float)
        for theta in theta_range:
            x = -1
            for i in scales:
                x += 1
                y = -1
                for j in scales:
                    y += 1
                    filter_gabor[y, x] = self.gabor_single(i, j, f0, theta)
            # filtered_image = (cv2.filter2D(image, -1, filter_gabor))
            filter_real = np.real(filter_gabor)
            filter_imag = np.imag(filter_gabor)
            result_temp_real = cv2.filter2D(image, -1, filter_real)
            # result_temp_real = np.convolve(image, filter_real, 'same')
            result_temp_imag = cv2.filter2D(image, -1, filter_imag)
            filtered_image = result_temp_real + 1j * result_temp_imag
            filtered_images.append(abs(filtered_image))

        return filtered_images

    def LGBP_feature(self, image):
        filtered_images = self.gabor_filter(image)
        features = []

        for i in range(self.orients):
            feature = self.lbp.__call__(filtered_images[i])
            features.append(feature)
        # try:
        #     row, col = np.shape(features)
        #     total = row * col * len(filtered_images)
        # except:
        #     row, col, dim = np.shape(features)
        #     total = row * col * dim * len(filtered_images)
        # features_out = np.reshape(features, [1, total])
        return np.asarray(features)

    def compute(self,X,y):
        features = []
        for x in X:
            x = np.asarray(x)
            h = self.LGBP_feature(x)
            features.append(h)
        return features

    def extract(self,X):
        X = np.asarray(X)
        return self.LGBP_feature(X)

class LGBP_single(AbstractFeature):
    def __init__(self):
        AbstractFeature.__init__(self)
        self.block_size = 16
        self.lbp = VarLBP()

    def gabor_transfer(self, image):
        Sx = 2
        Sy = 4
        f = 16
        theta = np.pi * 2 / 3
        Gabor = np.zeros([2*Sx+1, 2*Sy+1], dtype=np.float)
        # Gabor = []
        # Gabor_temp = np.zeros([1, Sy*2+1])

        for x in range(-Sx,Sx+1,1):
            for y in range(-Sy,Sy+1,1):
                xPrime = x * np.cos(theta) - y * np.sin(theta)
                yPrime = x * np.sin(theta) + y * np.cos(theta)
                Gabor[Sx+x, Sy+y] = np.exp(-0.5 * (np.power(xPrime/Sx, 2) + np.power(yPrime/Sy, 2))) \
                                   * np.sin(np.pi * 2 * f * xPrime)

        image_filtered = cv2.filter2D(image, -1, Gabor)
        # image_out = np.ndarray([112, 92], dtype=int)
        return abs(image_filtered)

    def extract_features(self, image):
        feature_gabor = self.gabor_transfer(image)
        feature = self.lbp.__call__(feature_gabor)
        return feature

    def compute(self,X,y):
        features = []
        for x in X:
            x = np.asarray(x)
            h = self.extract_features(x)
            features.append(h)
        return features

    def extract(self,X):
        X = np.asarray(X)
        return self.extract_features(X)


if __name__ == "__main__":
    lg = LGBP_single()
    image = cv2.imread('0.png')
    fea = lg.compute(image,1)
    print fea
    # filtered = lg.gabor_transfer(image)
    # cv2.imshow('a', filtered)
    # cv2.waitKey(30000)
