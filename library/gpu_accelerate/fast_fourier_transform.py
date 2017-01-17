__author__ = 'mac'

from pyfft.cl import Plan
import numpy
import pyopencl as cl
import pyopencl.array as cl_array
import time


class CachedQueueFFT:
    """Stores device, context, and queue information. Discards Convolvers
       after use to avoid hogging GPU memory and crashing drivers."""
    def __init__(self):
        device = cl.get_platforms()[0].get_devices(cl.device_type.GPU)
        self.ctx = cl.Context(devices=device)
        self.queue = cl.CommandQueue(self.ctx)

    def fast_fourier_transform(self, image_matrix):
        # instance the class  FastFourierTransform 's object
        fft = FastFourierTransform(image_matrix.shape, image_matrix, self.queue)
        fft.fourier_transform()


class FastFourierTransform:
    def __init__(self, in_scale, in_matrix, queue):
        self.scale = tuple(in_scale)
        # create plan
        self.plan = Plan(self.scale, queue=queue)
        # prepare data
        self.data = in_matrix
        self.gpu_data = cl_array.to_device(queue, self.data)

    def fourier_transform(self):
        # forward transform
        self.plan.execute(self.gpu_data.data)
        # print self.gpu_data.get()
        # inverse transform
        self.plan.execute(self.gpu_data.data, inverse=True)
        result_ = self.gpu_data.get()
        print(result_)
        error = numpy.abs(numpy.sum(numpy.abs(self.data) - numpy.abs(result_)) / self.data.size)
        if error > 1e-6:
            s = 'error occurs'
            raise ValueError('invalid value: %s' % s)
        return result_


def fft_transform_(matrix=None):
    if type(matrix) is not numpy.ndarray:
        matrix = numpy.array(matrix, dtype=numpy.float)
    fft_test = CachedQueueFFT()
    fft_test.fast_fourier_transform(matrix)

if __name__ == "__main__":
    fourier_data_test = [[3, 1, 1, 4, 8, 2, 1, 3],
                         [4, 2, 1, 1, 2, 1, 2, 3],
                         [4, 4, 4, 4, 3, 2, 2, 2],
                         [9, 8, 3, 8, 9, 0, 0, 0],
                         [9, 3, 3, 9, 0, 0, 0, 0],
                         [0, 9, 0, 8, 0, 0, 0, 0],
                         [3, 0, 8, 8, 9, 4, 4, 4],
                         [5, 9, 8, 1, 8, 1, 1, 1]]
    start = time.time()
    for x in xrange(1):
        fft_transform_(fourier_data_test)
        x += 1
    print(time.time() - start)

    start_ = time.time()
    for x in xrange(1):
        matrix_ = numpy.array(fourier_data_test, dtype=numpy.float)
        result_numpy = numpy.fft.fft(matrix_)
        print result_numpy
    print(time.time() - start_)