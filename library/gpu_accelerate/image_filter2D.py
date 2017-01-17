#!/usr/bin/env python
# -*- coding:utf-8 -*-
import pyopencl as cl
import sys
import PIL.Image as Image  # Python Image Library (PIL)
import numpy
from numpy import *
import PIL

#  Create an OpenCL context on the first available platform using
#  either a GPU or CPU depending on what is available.


class GpuFilter(object):

    def __init__(self):
        pass

    @staticmethod
    def create_context():
        platforms = cl.get_platforms()
        if len(platforms) == 0:
            print "Failed to find any OpenCL platforms."
            return None
        # Next, create an OpenCL context on the first platform.  Attempt to
        # create a GPU-based context, and if that fails, try to create
        # a CPU-based context.
        devices = platforms[0].get_devices(cl.device_type.GPU)
        if len(devices) == 0:
            print "Could not find GPU device, trying CPU..."
            devices = platforms[0].get_devices(cl.device_type.CPU)
            if len(devices) == 0:
                print "Could not find OpenCL GPU or CPU device."
                return None
        # Create a context using the first device
        ctx = cl.Context([devices[0]])
        return ctx, devices[0]

    #  Create an OpenCL program from the kernel source file

    @staticmethod
    def create_program(ctx, dev, file_name):
        kernel_file = open(file_name, 'r')
        kernel_str = kernel_file.read()

        # Load the program source
        prg = cl.Program(ctx, kernel_str)

        # Build the program and check for errors
        prg.build(devices=[dev])
        return prg

    #  Load an image using the Python Image Library and create an OpenCL
    #  image out of it
    @staticmethod
    def load_image(ctx, file_name):
        im = Image.open(file_name)
        # Make sure the image is RGBA formatted
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        # Convert to uint8 buffer
        buf = im.tobytes()
        cl_image_format = cl.ImageFormat(cl.channel_order.RGBA, cl.channel_type.UNORM_INT8)

        cl_image = cl.Image(ctx, cl.mem_flags.READ_ONLY | cl.mem_flags.COPY_HOST_PTR,
                            cl_image_format, im.size, None, buf)
        return cl_image, im.size

    #  Save an image using the Python Image Library (PIL)
    @staticmethod
    def image_convert(buf, img_size):
        im_result = Image.frombytes("RGBA", img_size, buf.tostring())
        # im.save(file_name)
        im_result = numpy.array(im_result)
        # Convert RGB to BGR
        return im_result[:, :, ::-1].copy()

    #  Round up to the nearest multiple of the group size
    @staticmethod
    def round_up(group_size, global_size):
        r = global_size % group_size
        if r == 0:
            return global_size
        else:
            return global_size + group_size - r


def gpu_filter(in_put='in.jpg'):
    gpu_filter_ = GpuFilter()
    image_objects = [0, 0]
    # if len(sys.argv) != 3:
    #     print "  : " + sys.argv[0] + " <inputImageFile> <outputImageFile>"
    #     exit()

    # Create an OpenCL context on first available platform
    context, device = gpu_filter_.create_context()

    if context is None:
        print "Failed to create OpenCL context."
        exit()

    # Create a command-queue on the first device available on the context that has been created
    command_queue = cl.CommandQueue(context, device)

    # Make sure the device supports images, otherwise exit
    if not device.get_info(cl.device_info.IMAGE_SUPPORT):
        print "OpenCL device does not support images."
        exit()

    # Load input image from file and load it into an OpenCL image object
    image_objects[0], img_size = gpu_filter_.load_image(context, in_put)
    # print image_objects[0], img_size

    # Create output image object
    cl_image_format = cl.ImageFormat(cl.channel_order.RGBA,
                                     cl.channel_type.UNORM_INT8)

    image_objects[1] = cl.Image(context,
                                cl.mem_flags.WRITE_ONLY,
                                cl_image_format,
                                img_size)

    # Create sampler for sampling image object
    sampler = cl.Sampler(context,
                         False,  # Non-normalized coordinates
                         cl.addressing_mode.CLAMP,
                         cl.filter_mode.NEAREST)

    # Create OpenCL program
    program = gpu_filter_.create_program(context, device, "ImageFilter2D.cl")

    # Call the kernel directly
    local_work_size = (16, 16)
    global_work_size = (gpu_filter_.round_up(local_work_size[0], img_size[0]),
                        gpu_filter_.round_up(local_work_size[1], img_size[1]))
    program.gaussian_filter(command_queue,
                            global_work_size,
                            local_work_size,
                            image_objects[0],
                            image_objects[1],
                            sampler,
                            numpy.int32(img_size[0]),
                            numpy.int32(img_size[1]))

    # Read the output buffer back to the Host
    cl_buffer = numpy.zeros(img_size[0] * img_size[1] * 4, numpy.uint8)
    origin = (0, 0, 0)
    region = (img_size[0], img_size[1], 1)
    cl.enqueue_read_image(command_queue, image_objects[1],
                          origin, region, cl_buffer).wait()
    print "Executed program successfully."

    # return the image matrix
    return gpu_filter_.image_convert(cl_buffer, img_size)

if __name__ == '__main__':

    pil_image = PIL.Image.open('in.jpg').convert('RGB')
    open_cv_image = numpy.array(pil_image)
    # Convert RGB to BGR
    print open_cv_image[:, :, ::-1].copy()
    print ('='*80)

    print gpu_filter('in.jpg')

