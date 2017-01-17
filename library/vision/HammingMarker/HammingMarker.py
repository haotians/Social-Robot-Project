import cv2

from numpy import mean, binary_repr, zeros
from numpy.random import randint
from scipy.ndimage import zoom

from HammingCoding import encode, HAMMINGCODE_MARKER_POSITIONS

MARKER_SIZE = 7


class HammingMarker(object):
    def __init__(self, id, contours=None):
        self.id = id
        self.contours = contours

    def __repr__(self):
        return '<Marker id={} center={}>'.format(self.id, self.center)

    @property
    def center(self):
        if self.contours is None:
            return None
        pos_array = mean(self.contours, axis=0).flatten()
        return (int(pos_array[0]), int(pos_array[1]))

    @property
    def upperleft(self):
        if self.contours is None:
            return None
        pos_array = self.contours[0][0]
        # print self.contours
        for i in range(3):
            if self.contours[i+1][0][0] < pos_array[0] and self.contours[i+1][0][1] < pos_array[1]:
                pos_array = self.contours[i+1][0]
        return (int(pos_array[0]), int(pos_array[1]))

    def generate_image(self):
        img = zeros((MARKER_SIZE, MARKER_SIZE))
        img[1, 1] = 255  # set the orientation marker
        for index, val in enumerate(self.hamming_code):
            coords = HAMMINGCODE_MARKER_POSITIONS[index]
            if val == '1':
                val = 255
            img[coords[0], coords[1]] = int(val)
        # return img
        return zoom(img, zoom=50, order=0)

    def draw_contour(self, img, color=(0, 255, 0), linewidth=5):
        cv2.drawContours(img, [self.contours], -1, color, linewidth)

    def highlite_marker(self, img, contour_color=(0, 255, 0), text_color=(255, 0, 0), linewidth=6,
                        potential_flag=0):
        if potential_flag == 0:
            self.draw_contour(img, color=contour_color, linewidth=linewidth)
            # print "bazinga: ", self.contours[0][0]
            cv2.putText(img, "ID:"+str(self.id), self.upperleft, cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
            # cv2.putText(img, "ID:"+str(self.id), self.center, cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)
        else:
            self.draw_contour(img, color=(255, 255, 0), linewidth=linewidth)
            cv2.putText(img, "Potential marker", self.upperleft, cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

        # print "id :", self.id
        # return self.id

    def generate(self):
        id = randint(4096)
        return HammingMarker(id)

    @property
    def id_as_binary(self):
        return binary_repr(self.id, width=12)

    @property
    def hamming_code(self):
        return encode(self.id_as_binary)
