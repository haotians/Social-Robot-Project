import cv2
from numpy import *
import numpy as np
import math


from HammingCoding import decode, extract_hamming_code
from HammingMarker import MARKER_SIZE, HammingMarker
print_debug = 0
BORDER_COORDINATES = [
    [0, 0], [0, 1], [0, 2], [0, 3], [0, 4], [0, 5], [0, 6], [1, 0], [1, 6], [2, 0], [2, 6], [3, 0],
    [3, 6], [4, 0], [4, 6], [5, 0], [5, 6], [6, 0], [6, 1], [6, 2], [6, 3], [6, 4], [6, 5], [6, 6],
]

ORIENTATION_MARKER_COORDINATES = [[1, 1], [1, 5], [5, 1], [5, 5]]

min_size = 20 # number of points
lernal_size = 3
kernal = np.ones((lernal_size, lernal_size), np.uint8)
thresh_size = (min_size/4)*2 + 1
min_side_length = 20


def detect_markers(img, cam_matrix, dist):
    width, height, _ = img.shape
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(gray, 10, 100)

    # # get binary image with ADAPTIVE_THRESH_GAUSSIAN filter
    # binary = cv2.adaptiveThreshold(gray, 255, cv2.cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C,
    #                                cv2.cv.CV_THRESH_BINARY_INV, thresh_size, thresh_size/3)
    #
    # # remove the noise
    # binary_refine = cv2.morphologyEx(binary, cv2.cv.CV_MOP_OPEN, kernal)
    #
    # # find contors
    # (contours, _) = cv2.findContours(binary_refine.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)

    contours, hierarchy = cv2.findContours(edges.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    # We only keep the long enough contours
    min_contour_length = min(width, height) / 50
    contours = [contour for contour in contours if len(contour) > min_contour_length]

    # init marker coord
    warped_size = 49
    canonical_marker_coords = np.array(((0, 0),
                                        (warped_size - 1, 0),
                                        (warped_size - 1, warped_size - 1),
                                        (0, warped_size - 1)),
                                        dtype='float32')

    markers_list = []
    potential_markers_list = []
    distance = [0, 0, 0]  # is this going to be list?

    for contour in contours:
        test_result = 50
        # approximate the contours with minimum polygens
        approx_curve = cv2.approxPolyDP(contour, len(contour) * 0.01, True)
        # only poly has 4 lines and convex shape will be considered
        if not (len(approx_curve) == 4 and cv2.isContourConvex(approx_curve)):
            continue
        # print "approx_curve: \n", approx_curve

        tmp_width_1 = math.fabs(approx_curve[0][0][0] - approx_curve[1][0][0])
        tmp_width_2 = math.fabs(approx_curve[0][0][1] - approx_curve[1][0][1])
        tmp_length_1= math.fabs(approx_curve[0][0][0] - approx_curve[2][0][0])
        tmp_length_2= math.fabs(approx_curve[0][0][1] - approx_curve[2][0][1])
        tmp_di_1= math.fabs(approx_curve[0][0][0] - approx_curve[3][0][0])
        tmp_di_2= math.fabs(approx_curve[0][0][1] - approx_curve[3][0][1])
        tmp_width = (tmp_width_1**2 + tmp_width_2**2)**0.5
        tmp_length = (tmp_length_1**2 + tmp_length_2**2)**0.5
        tmp_di = (tmp_di_1**2 + tmp_di_2**2)**0.5
        tmp4 = ((approx_curve[1][0][0] - approx_curve[2][0][0])**2 +\
               (approx_curve[1][0][1] - approx_curve[2][0][1])**2)**0.5
        tmp5 = ((approx_curve[1][0][0] - approx_curve[3][0][0])**2 +\
               (approx_curve[1][0][1] - approx_curve[3][0][1])**2)**0.5
        tmp6 = ((approx_curve[2][0][0] - approx_curve[3][0][0])**2 +\
               (approx_curve[2][0][1] - approx_curve[3][0][1])**2)**0.5

        # if print_debug == 1:
        # print "tmp_length, tmp_width, tmp_di, tmp4, tmp5, tmp6 \n", tmp_length, tmp_width, tmp_di, tmp4, tmp5, tmp6
        # if tmp_length < 30 or tmp_width < 30 or tmp_di < 30 or tmp4 < 30 or tmp5 < 30 or tmp6 < 30:
        #     continue

        if np.min([tmp_length, tmp_width, tmp_di, tmp4, tmp5, tmp6]) < 30:
            continue

        # tmp_length= \
        #     ((approx_curve[1][0][0] - approx_curve[2][0][0])**2 + (approx_curve[1][0][1] - approx_curve[2][0][1])**2)**0.5
        # print "len(approx_curve)-shape", approx_curve.shape
        if print_debug == 1:
            print "approx_curve\n", approx_curve
        # tmp1 = np.mean(np.std(approx_curve, axis=2))
        # tmp2 = np.mean(np.std(approx_curve, axis=0))
        # print "stardard deviation \n", tmp1, tmp2
        # if (tmp1 < 40) or (tmp2 < 40):
        #     print "round 2"
        #     continue
        # if tmp_length == 0 or tmp_width == 0 or tmp_length < 30 or tmp_width < 30 or tmp_di < 30:
        #     print "tmp_length = 0"
        #     continue
        # elif (tmp_length/tmp_width > 1.25) or (tmp_length/tmp_width < 0.75):
        #     print "wrong ratio"
        #     continue
        # sorted convex points in anti-clockwise order

        sorted_curve = np.array(cv2.convexHull(approx_curve, clockwise=False),
                                dtype='float32')
        # Calculates a perspective transform from four pairs of the corresponding points.
        persp_transf = cv2.getPerspectiveTransform(sorted_curve, canonical_marker_coords)
        warped_img = cv2.warpPerspective(img, persp_transf, (warped_size, warped_size))
        warped_gray = cv2.cvtColor(warped_img, cv2.COLOR_BGR2GRAY)

        # _, warped_bin = cv2.threshold(warped_gray, 127, 255, (cv2.THRESH_BINARY))
        # ------ adaptive threshold for mean or gaussian, replace ADAPTIVE_THRESH_MEAN_C with ADAPTIVE_THRESH_GAUSSIAN_C
        # ------ blocksize for calculate threshold, constant_c subtracted from the mean or weighted mean
        # block_size = 11
        # constant_c = 0
        # warped_bin = cv2.adaptiveThreshold(warped_gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, block_size,
        #                                    constant_c)

        # ------ Otsu's threshold
        ret2, warped_bin = cv2.threshold(warped_gray, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        # ------ Otsu's threshold after Gaussian
        # blur_img = cv2.GaussianBlur(warped_gray, (5, 5), 0)
        # ret3, warped_bin = cv2.threshold(blur_img, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #------------ these four algorithms should be chosen according to AE if it is available, or based on further tests
        # print "00 !! warped_bin.shape \n", warped_bin.shape
        # print "warped_bin \n", warped_bin
        marker = warped_bin.reshape(
            [MARKER_SIZE, warped_size / MARKER_SIZE, MARKER_SIZE, warped_size / MARKER_SIZE]
        )
        # print "1 marker \n", marker
        # print "marker.shape \n", marker.shape
        marker = marker.mean(axis=3).mean(axis=1)
        # marker = marker.mean(axis=3)
        # print "2 marker \n", marker
        # marker = marker.mean(axis=1)
        # print "2.5 marker \n", marker
        counter = 0
        for lines in marker:
            for ele in lines:
                if (abs(ele - 127) < 40):
                    counter += 1
                    # print "ele \n", ele
        # print "counter: \n", counter
        potential_flag = 0
        if counter >= 2:
            potential_flag = 1
        marker[marker < 127] = 0
        marker[marker >= 127] = 1
        # print "3 marker \n", marker

        try:
            # try to get the valid marker and the orientation marker positions
            potential_marker = validate_potential_marker(marker)
            # print "Front, In try,,, potential_marker : \n", potential_marker
            marker = validate_and_turn(potential_marker)
            if print_debug == 1:
                print "potential_flag : ", potential_flag
            # print "marker \n", marker
            if marker != [] and potential_flag == 0:
                potential_marker = []
                R, T = camera_pose_estimate(gray, sorted_curve, cam_matrix, dist)
                distance = kinematics_coordinate(0, 8, R, T)
                hamming_code = extract_hamming_code(marker)
            # decode the pattern and return the ID
                marker_id = int(decode(hamming_code), 2)
                markers_list.append(HammingMarker(id=marker_id, contours=approx_curve))
            else:
                marker = []
                potential_markers_list.append(HammingMarker(id=0, contours=approx_curve))


            # calculate R and T for each marker

            # using marker to detect hamming code pattern
            # if marker != [] and potential_flag == 0:
            #     hamming_code = extract_hamming_code(marker)
            # # decode the pattern and return the ID
            #     marker_id = int(decode(hamming_code), 2)
            #     markers_list.append(HammingMarker(id=marker_id, contours=approx_curve))

            # if marker != [] and potential_marker != []:
            #     print "!!!!!!!!!!!!!!!"
            #     cv2.waitKey(1000000)
        except ValueError:
            # something goes wrong and drop this marker
            continue
    # for debug false marker
    # if markers_list != [] or potential_markers_list != []:
    #     print "debug"
    #     cv2.waitKey(1000000)
    return markers_list, potential_markers_list, distance


def validate_and_turn(marker):
    # first, lets make sure that the border contains only zeros
    # for crd in BORDER_COORDINATES:
    #     if marker[crd[0], crd[1]] != 0.0:
    #         raise ValueError('Border contains not entirely black parts.')
    # search for the corner marker for orientation and make sure, there is only 1
    orientation_marker = None
    for crd in ORIENTATION_MARKER_COORDINATES:
        marker_found = False
        if marker[crd[0], crd[1]] == 1.0:
            marker_found = True
        if marker_found and orientation_marker:
            marker = []
            return marker
            #raise ValueError('More than 1 orientation_marker found.')
        elif marker_found:
            orientation_marker = crd
    if not orientation_marker:
        marker = []
        return marker
        # raise ValueError('No orientation marker found.')
    rotation = 0
    if orientation_marker == [1, 5]:
        rotation = 1
    elif orientation_marker == [5, 5]:
        rotation = 2
    elif orientation_marker == [5, 1]:
        rotation = 3
    marker = np.rot90(marker, k=rotation)
    return marker


def validate_potential_marker(marker):  ## add range check!!
    counter = 0
    for crd in BORDER_COORDINATES:
        if marker[crd[0], crd[1]] != 0.0:
            if print_debug == 1:
                print "debug border check-- not black"
            # raise ValueError('Border contains not entirely black parts.')
        else:
            counter += 1
        # print "counter: ", counter
    # for 1000+ lux, pure black border may appear to be not black
    if counter < 15:
        raise ValueError('Border contains not entirely black parts.')
    return marker


def camera_pose_estimate(gray, corners, cam_matrix, dist):
    # criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.01)

    criteria = (cv2.TERM_CRITERIA_MAX_ITER, 30, 0.1)
    # print corners
    corners_reshape = objp = np.zeros((4,2), np.float32)
    corners_reshape[0] = corners[0]
    corners_reshape[1] = corners[1]
    corners_reshape[2] = corners[2]
    corners_reshape[3] = corners[3]

    # corners2 = cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

    # objp = np.zeros((4,3), np.float32)
    # objp[0] = [-4.5, -4.5, 0.0]
    # objp[1] = [-4.5, 4.5, 0.0]
    # objp[2] = [4.5, 4.5, 0.0]
    # objp[3] = [4.5, -4.5, 0.0]


    marker_size = 1.73  #  change this value for different marker sizes(cm)
    object_points = np.zeros((4,3), np.float32)
    # object_points[0] = [-4.25, -4.25, 0.0]
    # object_points[1] = [-4.25, 4.25, 0.0]
    # object_points[2] = [4.25, 4.25, 0.0]
    # object_points[3] = [4.25, -4.25, 0.0]
    object_points[0] = [-1, -1, 0.0]
    object_points[1] = [-1, 1, 0.0]
    object_points[2] = [1, 1, 0.0]
    object_points[3] = [1, -1, 0.0]
    object_points = object_points * marker_size
    axis = np.float32([[3,0,0], [0,3,0], [0,0,-3]]).reshape(-1,3)
    # print "corners_reshape:\n", corners_reshape
    k_vector = np.zeros((1,4),np.float32)

    R, T, inliers = cv2.solvePnPRansac(object_points, corners_reshape, cam_matrix, dist)
    # print "R: \n", R
    # print "T: \n", T
    matrix_3x3, jacob = cv2.Rodrigues(R)
    # print "T: \n", T
    # print "|T|: \n", (T[0]**2 + T[1]**2 + T[2]**2)**0.5*10
    # print "R[0]: \n", R[0]
    # print "matrix_3x3: \n", matrix_3x3
    return R, T


def draw(img, corners, imgpts):
    corner = tuple(corners[0].ravel())
    img = cv2.line(img, corner, tuple(imgpts[0].ravel()), (255,0,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[1].ravel()), (0,255,0), 5)
    img = cv2.line(img, corner, tuple(imgpts[2].ravel()), (0,0,255), 5)
    return img


def kinematics_coordinate(alpha, beta, R, translation_vector):
    # r_hv, alpha -- horizontal-vertical
    # r_ud, beta  -- up-down, counter-clockwise plus, clockwise minus
    # r_hv >= r_ud for now
    # h -- distance from camera to ground

    # a -- kinematic
    # b -- camera
    # c -- marker
    matrix_3x3, jacob = cv2.Rodrigues(R)

    # alpha += 270
    # beta += 270
    r_hv = 170
    r_ud = 0
    h = 650
    r_z = np.zeros((3,3), np.float32)
    r_z[0][0] =  math.cos(alpha / 360.0 * 2 * math.pi)
    r_z[0][1] = -math.sin(alpha / 360.0 * 2 * math.pi)
    r_z[1][0] =  math.sin(alpha / 360.0 * 2 * math.pi)
    r_z[1][1] =  math.cos(alpha / 360.0 * 2 * math.pi)
    r_z[2][2] =  1
    #

    # result = np.zeros((3, 1))
    # r_ab = mat(r_ab)
    # result = np.dot( r_ab.I, 10*translation_vector - t_ab)

    beta += 270
    r_x = np.zeros((3,3), np.float32)
    r_x[0][0] =  1
    r_x[1][1] =  math.cos(beta / 360.0 * 2 * math.pi)
    r_x[1][2] = -math.sin(beta / 360.0 * 2 * math.pi)
    r_x[2][1] =  math.sin(beta / 360.0 * 2 * math.pi)
    r_x[2][2] =  math.cos(beta / 360.0 * 2 * math.pi)

    r_ab = np.dot(r_z, r_x)

    t_ab = np.zeros((3, 1), np.float32)
    t_ab[0] = -r_hv * math.sin(alpha / 360.0 * 2 * math.pi)
    t_ab[1] = r_hv * math.cos(alpha / 360.0 * 2 * math.pi)
    t_ab[2] = h + r_hv * math.sin((beta -270.0) / 360.0 * 2 * math.pi)
    result = np.dot(r_ab, 10.0 * translation_vector) + t_ab

    horizontal_x = result[0][0] / 1000
    vertical_y = result[1][0] / 1000
    z = result[2][0] / 1000

    # print "r_z \n", r_z
    # print "r_x \n", r_x
    # print "t_ab \n", t_ab
    # print "r_ab \n", r_ab
    # print "r_ab.I \n", r_ab.I
    # print "10*translation_vector :\n", 10*translation_vector
    # print "horizontal_x: \n", horizontal_x
    # print "vertical_y: \n", vertical_y
    # print "z: \n", z

    # for kinematic coordinate, this is important!!
    return [vertical_y, -horizontal_x, z]
