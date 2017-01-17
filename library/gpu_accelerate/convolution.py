"""
Provides a GPU enhanced convolution function equivalent to 
scipy.signal.convolve for 2d and 3d arrays, and can apply one kernel
to many arrays in parallel.
"""

from pyfft.cl import Plan
import numpy
import time
import pyopencl as cl
import pyopencl.array as cl_array
import PIL
from PIL import Image


def get_power_of_two(value):
    return int(numpy.power(2, numpy.ceil(numpy.log2(value))))


class CachedQueueConvolve:
    """Stores device, context, and queue information. Discards Convolvers 
       after use to avoid hogging GPU memory and crashing drivers."""
    def __init__(self):
        device = cl.get_platforms()[0].get_devices(cl.device_type.GPU)
        self.ctx = cl.Context(devices=device)
        self.queue = cl.CommandQueue(self.ctx)
        
    def convolution(self, image_matrix, kernel, mode='valid'):
        # instance the class Convolve 's object
        convolve = Convolve(image_matrix[0].shape, kernel.shape, image_matrix.shape[0], self.ctx, self.queue)
        return convolve.convolution(image_matrix, kernel, mode)


class Convolve:
    """ Class that computes the necessary information to perform a
    convolution and provides the actual convolution function. Can handle
    2d or 3d convolutions. """
    
    def __init__(self, in_size, kernel_size, batch_size, context, queue):
        self.sizes = []
        for i in xrange(len(in_size)):
            self.sizes.append(get_power_of_two(in_size[i]+kernel_size[i]+1))
        self.sizes = tuple(self.sizes)
        
        self.ctx = context
        self.queue = queue
        self.plan = Plan(self.sizes, queue=self.queue)
        self.in_array = cl.array.zeros(self.queue, (batch_size, self.sizes[0], self.sizes[1], self.sizes[2]),
                                       numpy.complex64)
        self.kernel = cl.array.zeros(self.queue, (batch_size, self.sizes[0], self.sizes[1], self.sizes[2]),
                                     numpy.complex64)
        self.result_buffer = numpy.zeros(self.in_array.shape, numpy.complex64)
        self.kernel_center = []
        for i in xrange(len(kernel_size)):
            self.kernel_center.append(kernel_size[i]/2)
        self.kernel_center = tuple(self.kernel_center)

        self.halves = []
        for i in xrange(len(kernel_size)):
            self.halves.append(numpy.ceil(kernel_size[i]/2.0))
        self.halves = tuple(self.halves)

        self.padding_locations = []
        for i in xrange(len(self.sizes)):
            # without this if even kernels result in an incorrect edge in the result
            if kernel_size[i] % 2 == 0:
                self.padding_locations.append(-1*((in_size[i]-self.sizes[i])/2))
                self.padding_locations.append(-1*((self.sizes[i]-in_size[i])/2))
            else:
                self.padding_locations.append((self.sizes[i]-in_size[i])/2)
                self.padding_locations.append((in_size[i]-self.sizes[i])/2)
        self.padding_locations = tuple(self.padding_locations)
        
        self.valid_locations = []
        for i in xrange(len(self.sizes)):
            self.valid_locations.append(self.padding_locations[(i*2)] + self.halves[i] - 1)
            self.valid_locations.append(self.padding_locations[(i*2)] + self.halves[i] + in_size[i] - kernel_size[i])
        self.valid_locations = tuple(self.valid_locations)

        self.full_locations = []
        for i in xrange(len(self.sizes)):
            offset = self.sizes[i] - (in_size[i]+kernel_size[i]-1)
            self.full_locations.append(offset/2)
            self.full_locations.append(-offset/2)
        
        self.batch_size = batch_size
        
    def convolution(self, input_matrix, kernel, type_='valid'):
        in_array = numpy.zeros((self.batch_size, self.sizes[0], self.sizes[1], self.sizes[2]), numpy.complex64)
        in_array[:, self.padding_locations[0]:self.padding_locations[1],
                    self.padding_locations[2]:self.padding_locations[3],
                    self.padding_locations[4]:self.padding_locations[5]] = input_matrix

        self.in_array = cl.array.to_device(self.queue, in_array)

        kernel_buffer = numpy.zeros((self.batch_size, self.sizes[0], self.sizes[1], self.sizes[2]), numpy.complex64)

        kernel_buffer[:, :self.halves[0], :self.halves[1], :self.halves[2]] = \
            kernel[self.kernel_center[0]:, self.kernel_center[1]:, self.kernel_center[2]:]

        kernel_buffer[:, :self.halves[0], :self.halves[1], -self.kernel_center[2]:] = \
            kernel[self.kernel_center[0]:, self.kernel_center[1]:, :self.kernel_center[2]]

        kernel_buffer[:, :self.halves[0], -self.kernel_center[1]:, :self.halves[2]] = \
            kernel[self.kernel_center[0]:, :self.kernel_center[1], self.kernel_center[2]:]

        kernel_buffer[:, :self.halves[0], -self.kernel_center[1]:, -self.kernel_center[2]:] = \
            kernel[self.kernel_center[0]:, :self.kernel_center[1], :self.kernel_center[2]]

        if kernel.shape[0] > 1:
            kernel_buffer[:, -self.kernel_center[0]:, :self.halves[1], :self.halves[2]] = \
                kernel[:self.kernel_center[0], self.kernel_center[1]:, self.kernel_center[2]:]

            kernel_buffer[:, -self.kernel_center[0]:, :self.halves[1], -self.kernel_center[2]:] = \
                kernel[:self.kernel_center[0], self.kernel_center[1]:, :self.kernel_center[2]]

            kernel_buffer[:, -self.kernel_center[0]:, -self.kernel_center[1]:, :self.halves[2]] = \
                kernel[:self.kernel_center[0], :self.kernel_center[1], self.kernel_center[2]:]

            kernel_buffer[:, -self.kernel_center[0]:, -self.kernel_center[1]:, -self.kernel_center[2]:] = \
                kernel[:self.kernel_center[0], :self.kernel_center[1], :self.kernel_center[2]]

        self.kernel = cl.array.to_device(self.queue, kernel_buffer)

        # fourier transform, point wise multiply, then invert => convolution
        self.plan.execute(self.in_array.data, batch=self.batch_size)
        
        self.plan.execute(self.kernel.data, batch=self.batch_size)
        
        self.result_buffer = self.in_array * self.kernel
        self.plan.execute(self.result_buffer.data, inverse=True, batch=self.batch_size)
        result = self.result_buffer.get().astype(float)
                                 
        if type_ == 'same':
            return result[:,  self.padding_locations[0]:self.padding_locations[1], self.padding_locations[2]:
                          self.padding_locations[3], self.padding_locations[4]:self.padding_locations[5]]
        elif type_ == 'full':
            return result[:, self.full_locations[0]:self.full_locations[1], self.full_locations[2]:
                          self.full_locations[3], self.full_locations[4]:self.full_locations[5]]
        elif type_ == 'valid':
            return result[:, self.valid_locations[0]:self.valid_locations[1], self.valid_locations[2]:
                          self.valid_locations[3], self.valid_locations[4]:self.valid_locations[5]]


def gpu_convolution(batched=None, kernel_=None):
    cvl_test = CachedQueueConvolve()
    batched = numpy.array([batched], dtype=numpy.float)
    # print(batched)
    kernel_ = numpy.array([kernel_], dtype=numpy.float)
    # print(kernel_)
    result = cvl_test.convolution(batched, kernel_, 'valid')
    # print(result[0])
    return result[0]

    # for i in xrange(result.shape[0]):
    #     truth = signal.fftconvolve(batched[i], kernel_, 'valid')
    #     # print(result[i])
    #     print(numpy.any(numpy.abs(result[i] - truth) > 0.0001))

if __name__ == "__main__":
    pil_image = PIL.Image.open('in.jpg').convert('RGB')
    open_cv_image = numpy.array(pil_image)
    # Convert RGB to BGR
    open_cv_image = open_cv_image[:, :, ::-1].copy()
    print open_cv_image.shape
    kernel_test = [[1, 1, 1],
                   [1, 1, 0],
                   [1, 1, 1]]
    start = time.time()
    for x in xrange(11):
        result = gpu_convolution(open_cv_image, kernel_test)
        x += 1
    print(time.time() - start)
