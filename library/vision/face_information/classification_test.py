# Author: Haotian Shi, Last Modified Date: 2016-02-17
import numpy as np
import matplotlib.pyplot as plt
# # %matplotlib inline

print "lol"
# Make sure that caffe is on the python path:
caffe_root = '/home/haotians/Documents/caffe/'
import sys, os
sys.path.insert(0, caffe_root + 'python')
#
print sys.path
import caffe
import time
import cv2

def classification_test():

    caffe.set_mode_cpu()

    net = caffe.Net(caffe_root + 'face_models/deploy.prototxt',
                    caffe_root + 'face_models/model.caffemodel',
                    caffe.TEST)

    # # input preprocessing: 'data' is the name of the input blob == net.inputs[0]
    transformer = caffe.io.Transformer({'data': net.blobs['data'].data.shape})
    transformer.set_transpose('data', (2,0,1))
    transformer.set_mean('data', np.load('face_models/ilsvrc_2012_mean.npy').mean(1).mean(1)) # mean pixel
    transformer.set_raw_scale('data', 255)  # the reference model operates on images in [0,255] range instead of [0,1]
    transformer.set_channel_swap('data', (2,1,0))  # the reference model has channels in BGR order instead of RGB
    #
    # set net to batch size of 50
    input_size = 1
    net.blobs['data'].reshape(input_size, 3, 227, 227)

    path = caffe_root + 'examples/images/paper.jpg'

    net.blobs['data'].data[...] = transformer.preprocess('data', caffe.io.load_image(path))
    timer1 = time.time()
    out = net.forward()
    timer2 = time.time()
    print out
    print("Predicted class is #{}.".format(out['pool4'][0].argmax()))

    # load labels
    imagenet_labels_filename = caffe_root + 'data/ilsvrc12/synset_words.txt'
    try:
        labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')
    except:
        # !../data/ilsvrc12/get_ilsvrc_aux.sh
        labels = np.loadtxt(imagenet_labels_filename, str, delimiter='\t')

    # sort top k predictions from softmax output
    top_k = net.blobs['pool4'].data[0].flatten().argsort()[-1:-6:-1]
    print net.blobs['pool4'].data[0]
    print top_k
    print "result: "
    print "time cost: ",timer2 - timer1
    for i in range(5):
        print labels[top_k[i]]

    # plt.imshow(transformer.deprocess('data', net.blobs['data'].data[0]))
    import cv2
    img = cv2.imread(path)
    cv2.imshow("target",img)
    print "fini"

#helper show filter outputs
def show_filters(net):
	net.forward()
	plt.figure()
	filt_min, filt_max = net.blobs['conv'].data.min(), net.blobs['conv'].data.max()
	for i in range(3): # three feature map.
		plt.subplot(1,4,i+2)
		plt.title("filter #{} output".format(i))
		plt.imshow(net.blobs['conv'].data[0,i], vmin=filt_min, vmax=filt_max)
		plt.tight_layout()
		plt.axis('off')
		plt.show()

def generateBoundingBox(featureMap, scale):
    boundingBox = []
    stride = 32
    cellSize = 227
    #227 x 227 cell, stride=32
    for (x,y), prob in np.ndenumerate(featureMap):
       if(prob >= 0.85):
            boundingBox.append([float(stride * y)/ scale, float(x * stride)/scale, float(stride * y + cellSize - 1)/scale, float(stride * x + cellSize - 1)/scale, prob])
    #sort by prob, from max to min.
    #boxes = np.array(boundingBox)
    return boundingBox

def nms_average(boxes, overlapThresh=0.2):
    result_boxes = []
    if len(boxes) == 0:
        return []
    # initialize the list of picked indexes
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(boxes[:,4])

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

         # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        #area of i.
        area_i = np.maximum(0, x2[i] - x1[i] + 1) * np.maximum(0, y2[i] - y1[i] + 1)
        area_array = np.zeros(len(idxs) - 1)
        area_array.fill(area_i)
        # compute the ratio of overlap
        #overlap = (w * h) / (area[idxs[:last]]  - w * h + area_array)

        overlap = (w * h) / (area[idxs[:last]])
        delete_idxs = np.concatenate(([last],np.where(overlap > overlapThresh)[0]))
        xmin = 10000
        ymin = 10000
        xmax = 0
        ymax = 0
        ave_prob  = 0
        width = x2[i] - x1[i] + 1
        height = y2[i] - y1[i] + 1
        for idx in delete_idxs:
            ave_prob += boxes[idxs[idx]][4]
            if(boxes[idxs[idx]][0] < xmin):
                xmin = boxes[idxs[idx]][0]
            if(boxes[idxs[idx]][1] < ymin):
                ymin = boxes[idxs[idx]][1]
            if(boxes[idxs[idx]][2] > xmax):
                xmax = boxes[idxs[idx]][2]
            if(boxes[idxs[idx]][3] > ymax):
                ymax = boxes[idxs[idx]][3]
        if(x1[i] - xmin >  0.1 * width):
            xmin = x1[i] - 0.1 * width
        if(y1[i] - ymin > 0.1 * height):
            ymin = y1[i] - 0.1 * height
        if(xmax - x2[i]> 0.1 * width):
            xmax = x2[i]  + 0.1 * width
        if( ymax - y2[i] > 0.1 * height):
            ymax = y2[i] + 0.1 * height
        result_boxes.append([xmin, ymin, xmax, ymax, ave_prob / len(delete_idxs)])
        # delete all indexes from the index list that have
        idxs = np.delete(idxs, delete_idxs)

    # return only the bounding boxes that were picked using the
    # integer data type
    #result = np.delete(boxes[pick],np.where(boxes[pick][:, 4] < 0.9)[0],  axis=0)
    #print boxes[pick]
    return result_boxes


def nms_max(boxes, overlapThresh=0.3):
    if len(boxes) == 0:
        return []
    # initialize the list of picked indexes
    pick = []
    # grab the coordinates of the bounding boxes
    x1 = boxes[:,0]
    y1 = boxes[:,1]
    x2 = boxes[:,2]
    y2 = boxes[:,3]
    # compute the area of the bounding boxes and sort the bounding
    # boxes by the bottom-right y-coordinate of the bounding box
    area = (x2 - x1 + 1) * (y2 - y1 + 1)
    idxs = np.argsort(boxes[:,4])

    # keep looping while some indexes still remain in the indexes
    # list
    while len(idxs) > 0:
        # grab the last index in the indexes list and add the
        # index value to the list of picked indexes
        last = len(idxs) - 1
        i = idxs[last]
        pick.append(i)

        # find the largest (x, y) coordinates for the start of
        # the bounding box and the smallest (x, y) coordinates
        # for the end of the bounding box
        xx1 = np.maximum(x1[i], x1[idxs[:last]])
        yy1 = np.maximum(y1[i], y1[idxs[:last]])
        xx2 = np.minimum(x2[i], x2[idxs[:last]])
        yy2 = np.minimum(y2[i], y2[idxs[:last]])

         # compute the width and height of the bounding box
        w = np.maximum(0, xx2 - xx1 + 1)
        h = np.maximum(0, yy2 - yy1 + 1)
        #area of i.
        area_i = np.maximum(0, x2[i] - x1[i] + 1) * np.maximum(0, y2[i] - y1[i] + 1)
        area_array = np.zeros(len(idxs) - 1)
        area_array.fill(area_i)
        # compute the ratio of overlap
        overlap = (w * h) / (area[idxs[:last]]  - w * h + area_array)
        #overlap = (w * h) / (area[idxs[:last]])
        # delete all indexes from the index list that have
        idxs = np.delete(idxs, np.concatenate(([last],np.where(overlap > overlapThresh)[0])))

    # return only the bounding boxes that were picked using the
    # integer data type
    #result = np.delete(boxes[pick],np.where(boxes[pick][:, 4] < 0.9)[0],  axis=0)
    #print boxes[pick]
    return boxes[pick]

def convert_full_conv():
 # Load the original network and extract the fully connected layers' parameters.
    net = caffe.Net('deploy.prototxt',
                    'alexNet__iter_60000.caffemodel',
                    caffe.TEST)
    params = ['fc6', 'fc7', 'fc8_flickr']
    fc_params = {pr: (net.params[pr][0].data, net.params[pr][1].data) for pr in params}
    # Load the fully convolutional network to transplant the parameters.
    net_full_conv = caffe.Net('face_full_conv.prototxt',
                           'alexNet__iter_60000.caffemodel',
                              caffe.TEST)
    params_full_conv = ['fc6-conv', 'fc7-conv', 'fc8-conv']
    conv_params = {pr: (net_full_conv.params[pr][0].data, net_full_conv.params[pr][1].data) for pr in params_full_conv}
    for pr, pr_conv in zip(params, params_full_conv):
       conv_params[pr_conv][0].flat = fc_params[pr][0].flat  # flat unrolls the arrays
       conv_params[pr_conv][1][...] = fc_params[pr][1]
    net_full_conv.save('face_full_conv.caffemodel')


def face_detect(frame_name):

    caffe.set_mode_cpu()


    # net_full_conv = caffe.Net('./face_models/face_full_conv2.prototxt',
    #                       './face_models/face_full_conv.caffemodel',
    #                       caffe.TEST)
    # # load input and configure preprocessing
    # im = caffe.io.load_image("tmp.jpg")
    # transformer = caffe.io.Transformer({'data': net_full_conv.blobs['data'].data.shape})
    # transformer.set_mean('data', np.load(caffe_root + './face_models/ilsvrc_2012_mean.npy').mean(1).mean(1))
    # transformer.set_transpose('data', (2,0,1))

    scales = []
    factor = 0.793700526
    img = cv2.imread(frame_name)


    size0, size1, size2 = np.shape(img)

    min = 0
    max = 0
    if(size0 > size1):
        min = size1
        max = size0
    else:
        min = size0
        max = size1
    delim = 2500/max
    if(delim == 1):
        scales.append(1)
    elif(delim > 1):
        scales.append(delim)

    #scales.append(5)
    min = min * factor
    factor_count = 1
    while(min >= 227):
        scales.append(pow(factor,  factor_count))
        min = min * factor
        factor_count += 1
    total_boxes = []
    print 'size:', size0, size1
    print scales

    for scale in scales:
        #resize image
        scale_img = cv2.resize(img, (int(size0 * scale), int(size1 * scale)))

        size0_re, size1_re, size2_re = np.shape(scale_img)

        # cv2.imwrite("tmp.jpg", scale_img)

        # print 'size:', scale_img.size[0], scale_img.size[1]
        # modify the full_conv prototxt.
        prototxt = open('./face_models/face_full_conv.prototxt', 'r')
        new_line = ""
        for i, line in enumerate(prototxt):
            if i== 5:
                new_line += "input_dim: " + str(size1_re) + "\n"
            elif i== 6:
                new_line += "input_dim: " + str(size0_re) + "\n"
            else:
                new_line += line

        output = open('./face_models/face_full_conv2.prototxt', 'w')
        output.write(new_line)
        output.close()
        prototxt.close()


        im = scale_img

        net_full_conv = caffe.Net('./face_models/face_full_conv2.prototxt',
                                  './face_models/model.caffemodel',
                                  caffe.TEST)
        transformer = caffe.io.Transformer({'data': net_full_conv.blobs['data'].data.shape})
        transformer.set_mean('data', np.load('./face_models/ilsvrc_2012_mean.npy').mean(1).mean(1))
        transformer.set_transpose('data', (2,0,1))

        # make classification map by forward and print prediction indices at each location
        out = net_full_conv.forward_all(data=np.asarray([transformer.preprocess('data', im)]))
        #print out['prob'][0].argmax(axis=0)
        boxes = generateBoundingBox(out['prob'][0,1], scale)

        if(boxes):
            total_boxes.extend(boxes)

    #nms
    boxes_nms = np.array(total_boxes)
    true_boxes1 = nms_max(boxes_nms, overlapThresh=0.3)
    true_boxes = nms_average(np.array(true_boxes1), overlapThresh=0.07)
    print total_boxes
    #display the nmx bounding box in  image.
    # draw = ImageDraw.Draw(img)
    # print "width:", img.size[0], "height:",  img.size[1]
    # for box in true_boxes:
    #     draw.rectangle((box[0], box[1], box[2], box[3]), outline=(255,0,0) )
    #     font_path=os.environ.get("FONT_PATH", "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf")
    # ttFont = ImageFont.truetype(font_path, 20)
    # draw.text((box[0], box[1]), "{0:.2f}".format(box[4]), font=ttFont)

    return

# classification_test()
if __name__ == '__main__':
    # classification_test()
    face_detect('test9.jpg')