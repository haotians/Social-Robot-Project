# USAGE = """
# This program calibrates a camera.  To perform calibration, hold a checker board in front of the camera and move it around getting samples at all edges of the video feed and with different skewing angles and different distances.
# Press 'q' when enough samples have been collected, then the distortion matrices will be calculated.
# The program automatically performs the calculation after 50 samples have been collected to avoid excessive computation times.
# Requires extra parameter '1' to save calibration to avoid accidentally overriding previous calibration.
# """

import numpy as np
import cv2
import os
from CameraControl import open_camera, release_camera

CHESSBOARD_WIDTH = 9
CHESSBAORD_HEIGHT = 6

# class calibrate_class(object):
#     def __init__(self):
#         self.CalibrateCamera()

def CalibrateCamera(mode):#11
    # Get command line arguments
    # print USAGE
    homedir = os.getcwd()
    print homedir
    write = False
    # if len(sys.argv) == 2:
    #     if int(sys.argv[1]) == 1:
    #         write = True
    # if mode == 1:
    #     write = True
    # else:
    #     print "Warning, calibration results will not be saved. Run >python camera_calibration.py 1 to save results."

    # termination criteria for cornerSubPix function
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

    # prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
    objp = np.zeros((CHESSBOARD_WIDTH*CHESSBAORD_HEIGHT,3), np.float32)
    objp[:,:2] = np.mgrid[0:CHESSBOARD_WIDTH,0:CHESSBAORD_HEIGHT].T.reshape(-1,2)

    # Arrays to store object points and image points from all the images
    objpoints = [] # 3d point in real world space
    imgpoints = [] # 2d points in image plane.

    # Create video capture object
    camera_num = 0
    cap =None
    cap = open_camera(cap,None, camera_num)

    # Get video properties
    w = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.cv.CV_CAP_PROP_FRAME_HEIGHT))

    # Initialize counter for successful samples
    chess_samples = 0

    # frame skip
    frame_skip = 30

    # sample_take
    sample_take = 15

    # Collect imgpoints
    while cap.isOpened():
        # Read image and convert to grayscale for processing
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Find chessboard corners
        ret, corners = cv2.findChessboardCorners(gray, (CHESSBOARD_WIDTH, CHESSBAORD_HEIGHT),
                                                 cv2.cv.CV_CALIB_CB_ADAPTIVE_THRESH)
        # If chessboard corners found, add object points, image points (after refining them)
        if ret:
            # Increment counter for successful samples
            chess_samples += 1

            # Include fewer samples in calibration calculation to avoid excessive computation time
            if chess_samples % frame_skip == 0:
                print str(chess_samples/frame_skip)

                # Add chessboard points measured in the world
                objpoints.append(objp)

                # Refines corner detection
                cv2.cornerSubPix(gray, corners, (11, 11), (-1, -1), criteria)

                # Add detected corners pixel location
                imgpoints.append(corners)

            # Draw and display the corners
            cv2.drawChessboardCorners(img, (CHESSBOARD_WIDTH, CHESSBAORD_HEIGHT), corners, ret)

        # Display the video feed
        cv2.imshow('img', img)

        # Limit number of samples accumulated to avoid excessive computation times
        if chess_samples/frame_skip > sample_take:
            break

        # Quit on 'q' press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break

    # calibrate camera
    print "calibrating camera, I'm python and I'm slow..."
    ret, mtx, dist, _, _ = cv2.calibrateCamera(objpoints, imgpoints, (640,480),None,
                                                       (cv2.cv.CV_CALIB_USE_INTRINSIC_GUESS,
                                                       cv2.cv.CV_CALIB_FIX_PRINCIPAL_POINT))

    intrinsic_parameter = np.zeros((3,3), np.float32)
    # cam_matrix[0][0] = 887.58
    # cam_matrix[1][1] = 888.87
    # cam_matrix[0][2] = 363.10
    # cam_matrix[1][2] = 214.62

    # ------ for intrinsic cam0
    # intrinsic_parameter[0][0] = 611.52
    # intrinsic_parameter[1][1] = 611.30
    # intrinsic_parameter[0][2] = 306.63
    # intrinsic_parameter[1][2] = 214.23


    # rettmp, rvecstmp, tvecstmp = cv2.solvePnP(objpoints, imgpoints, intrinsic_parameter, dist)
    # print "tvecs : \n", tvecs
    print "finished\n"
    print "camera_matrix: \n", mtx
    print "dist \n", dist

    np.savetxt('calibration_matrix.txt', mtx,  fmt='%.8f')
    f = open('calibration_matrix.txt',  'a')
    np.savetxt(f, dist, fmt='%.8f')
    f.close()

    if write:
        write_to_file(mtx, dist)

    # **** View calibration results ****

    # Test calibration
    # while cap.isOpened():
    #
    #     ret, img = cap.read()
    #
    #     newImg = undistort(img, mtx, dist, w, h)
    #
    #     cv2.imshow('Original Image', img)
    #     cv2.imshow('Undistorted Image', newImg)
    #
    #     # Quit on 'q' press
    #     if cv2.waitKey(1) & 0xFF == ord('q'):
    #         break

    release_camera(cap)
    # cv2.destroyAllWindows()


def undistort(img, mtx, dist, w, h):
    # Undistort video
    newcameramtx, roi = cv2.getOptimalNewCameraMatrix(mtx, dist, (w, h), 1, (w, h))
    i = cv2.undistort(img, mtx, dist, None, newcameramtx)
    return i


# Write camera calibration data to a file
def write_to_file(mtx, dist):
    # Open a file is write mode
    matirx_file = open('cam_cal.txt', 'w')

    # Write mtx and dist matrix
    np.savez(matirx_file, mtx, dist)

    # Close file so it can be read from later
    matirx_file.close()

    print "calibration results written to file cam_cal.txt\n"


# Read camera calibration read from file
def read_from_file():
    # Open file to read from
    f = open('cam_cal.txt', 'r')

    # Read file
    npzfile = np.load(f)
    mtx = npzfile['arr_0']
    dist = npzfile['arr_1']

    # Close file
    f.close()

    print "Read camera calibration data file"

    return mtx, dist

# Run program, but not when called from an import statement
if __name__ == "__main__":
    CalibrateCamera(0)
