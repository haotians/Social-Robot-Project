#!/usr/bin/env python

import sys

import cv2

from library.vision import HammingMarker

if __name__ == '__main__':

    if len(sys.argv) > 1:
        if sys.argv[1] == '--generate':
            for i in range(int(sys.argv[2])):
                # default is random
                marker = HammingMarker.generate()
                cv2.imwrite('marker_images/marker_{}.png'.format(marker.id), marker.generate_image())
                print("Generated Marker with ID {}".format(marker.id))
        else:
            marker = HammingMarker(id=int(sys.argv[1]))
            cv2.imwrite('marker_images/marker_{}.png'.format(marker.id), marker.generate_image())
            print("Generated Marker with ID {}".format(marker.id))
    else:

        ID_code = 3
        marker = HammingMarker(ID_code)
        print marker.id
        target =  marker.generate_image()
        print target
        cv2.imshow('lol',target)
        cv2.waitKey(10)
        cv2.imwrite('marker_{}.png'.format(marker.id), target)
        cv2.waitKey(10)
        print("Generated Marker with ID {}".format(marker.id))
    print('Done!')
