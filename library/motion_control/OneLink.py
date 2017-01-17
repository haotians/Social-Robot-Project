
import numpy as np


class OneLink(object):

    # this is a object defining a link. It just contains necessary properties of a link
    def __init__(self):
        self.index = 0
        self.name = 'None'
        self.parent = 0
        self.angle = 0.0
        self.axis = np.array([0, 0, 0])
        self.offset = np.array([0.0, 0.0, 0.0])
        self.position = np.array([0.0, 0.0, 0.0])
        self.angle_limits = np.array([0, 0])
        self.orientation = np.eye(3)
