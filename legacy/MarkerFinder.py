import numpy as np
import math

import cv2

from library.vision.HammingMarker.MarkerDetect import detect_markers


def find_marker(image):

    # convert the image to grayscale, blur it, and detect edges
    gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    edged = cv2.Canny(gray, 35, 125)

    # find the contours in the edged image and keep the largest one;
    # we'll assume that this is our piece of paper in the image
    (cnts, _) = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    c = max(cnts, key = cv2.contourArea)

    # compute the bounding box of the of the paper region and return it
    return cv2.minAreaRect(c)


def distance_to_camera(knownWidth, focalLength, perWidth):
    #compute and return the distance from the maker to the camera
    return (knownWidth * focalLength) / perWidth


def get_valid_marker(img_gray,marker_possible):
    marker_final= []
    flag = False
    marker_dst = marker_possible[0]
    marker_size = len(marker_possible)

    warped_size = 49
    canonical_marker_coords = np.array(((0, 0),
                                        (warped_size - 1, 0),
                                        (warped_size - 1, warped_size - 1),
                                        (0, warped_size - 1)),
                                        dtype='float32')

    MARKER_SIZE = 7

    if marker_size == 0:
        return flag, marker_final
    else:
        for i in range(marker_size):
            persp_transf = cv2.getPerspectiveTransform(marker_possible[i], canonical_marker_coords)
            warped_img = cv2.warpPerspective(img_gray, persp_transf, (warped_size, warped_size))
            _, warped_bin = cv2.threshold(warped_img, 125, 255,(cv2.THRESH_BINARY, cv2.THRESH_OTSU))

            marker = warped_bin.reshape(
            [MARKER_SIZE, warped_size / MARKER_SIZE, MARKER_SIZE, warped_size / MARKER_SIZE])

            marker = marker.mean(axis=3).mean(axis=1)
            marker[marker < 127] = 0
            marker[marker >= 127] = 1


def main():

    # Create video capture object
    camera_num = 1
    cap = cv2.VideoCapture(camera_num)
    cap.set(3, 640)
    cap.set(4, 480)

    # camera_matrix
    cam_matrix = np.zeros((3,3), np.float32)
    cam_matrix[0][0] = 887.58
    cam_matrix[1][1] = 888.87
    cam_matrix[0][2] = 363.10
    cam_matrix[1][2] = 214.62

    min_size = 20 # number of points
    lernal_size = 3
    kernal = np.ones((lernal_size, lernal_size), np.uint8)
    thresh_size = (min_size/4)*2 + 1
    min_side_length = 20


    while cap.isOpened():

        # Read image and convert to grayscale for processing
        ret, img = cap.read()

        markers = detect_markers(img, cam_matrix)

        for marker in markers:
            marker.highlite_marker(img)

        cv2.imshow('Test Frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def marker_finder(img):

    marker_possible = []
    min_size = 20 # number of points
    lernal_size = 3
    kernal = np.ones((lernal_size, lernal_size), np.uint8)
    thresh_size = (min_size/4)*2 + 1
    min_side_length = 20

    # convert to gray image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # get binary image with ADAPTIVE_THRESH_GAUSSIAN filter
    binary = cv2.adaptiveThreshold(gray, 255, cv2.cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C,
                          cv2.cv.CV_THRESH_BINARY_INV, thresh_size,
                          thresh_size/3)

    # remove the noise
    binary_refine = cv2.morphologyEx(binary, cv2.cv.CV_MOP_OPEN,kernal)

    # find contors
    (cnts, _) = cv2.findContours(binary_refine.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    # find vaild contors
    count = 0
    cnt_refine2 = []

    cnt_refine1 = []
    max = len(cnts)
    # loop over all the contours
    for i in range(max):
        # contours size should be large than something
        if len(cnts[i]) > 2*min_size:

            eps = len(cnts[i])*0.01
            # use new ploy boundary to approximate the found contours
            # based on Ramer-Douglas-Peucker(RDP) algorithm
            cnt_refine2 = cv2.approxPolyDP(cnts[i], eps, True)
            # we want four lines only
            if len(cnt_refine2) != 4:
                continue

            # we want convex shape
            if not cv2.isContourConvex(cnt_refine2):
                continue

            # Ensure that the distance between consecutive points is large enough
            min_distance = 20
            min_side = 0
            for j in range(4):
                # 1-2 2-3 3-4 4-1
                point_side = cnt_refine2[j] - cnt_refine2[(j+1)%4]
                point_distance = math.sqrt(point_side[0][0] * point_side[0][0]
                                           + point_side[0][1] * point_side[0][1])
                if j == 0:
                    min_side = point_distance
                min_side = min(min_distance, point_distance)

            # get raid of samll boxes
            print "min_side: ", min_side

            if min_side < min_side_length:
                continue

            # sort the points in anti clock wise
            marker = np.array(cv2.convexHull(cnt_refine2, clockwise=False),
                         dtype='float32')
            # marker = cnt_refine2
            # vector_01 = marker[1] - marker[0]
            # vector_02 = marker[2] - marker[0]
            # # if clock-wise, then swipe
            # vector_cross = np.cross(vector_01, vector_02)
            # if vector_cross < 0:
            #     temp = marker[3]
            #     marker[3] = marker[2]
            #     marker[2] = temp

            marker_possible.append(marker)

    # find valid marker from the marker possible array
    get_valid_marker(gray, marker_possible)
    cv2.imshow("figure", binary_refine)
    cv2.waitKey(1)

# main code runs here
# this code apply a simple method to extract rect-shaped marker and return its distance
# in experiment, we have error about 20 to 30 mm
# need more accurate method

main()

# img_calib = cv2.imread("board.jpg")
#
# KNOWN_DISTANCE = 75
# KNOWN_WIDTH = 24
#
# marker = find_marker(img_calib)
# print "calib marker: ", marker
# focal_length = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH
#
#
# image_set = ["board.jpg","98.jpg","113.jpg","147.jpg","rotate.jpg"]
# # cv2.imshow("marker,img")
# for i in range(len(image_set)):
#     print i
#     # print image_set[i]
#     img = cv2.imread(image_set[i])
#     # print img
#     marker = find_marker(img)
#     print "test marker: ", marker
#
#     width = marker[1][0]
#     if width < marker[1][1]:
#         width = marker[1][1]
#     distance = distance_to_camera(KNOWN_WIDTH, focal_length, width)
#     print distance
#
#     # draw a bounding box around the image and display it
#     box = np.int0(cv2.cv.BoxPoints(marker))
#
#     cv2.drawContours(img, [box], -1, (0, 255, 0), 2)
#     cv2.putText(img, "%.2fmm" % (distance),
#                 (img.shape[1] - 200, img.shape[0] - 20), cv2.FONT_HERSHEY_SIMPLEX,
#                 2.0, (0, 255, 0), 3)
#     cv2.imshow("image", img)
#     cv2.waitKey(0)





