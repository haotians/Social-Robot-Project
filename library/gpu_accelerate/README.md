pyopencl_convolution
====================

A 2d/3d convolution implementation using PyOpenCL.

Can apply a kernel to many arrays at once. For instance, the following code applies the kernel to 20 arrays of shape (3,10,10):

    convolver = CachedQueueConvolver()
    batched_data = numpy.random.rand(20,3,10,10)
    kernel = numpy.random.rand(1,3,3)
    result = convolver.convolution(batched_data,kernel)
