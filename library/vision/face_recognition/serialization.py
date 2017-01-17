# Author: Yehang Liu, Last Modified Date: 2016-02-17

import cPickle


def save_model(filename, model):
    output = open(filename, 'wb')
    cPickle.dump(model, output)
    output.close()


def load_model(filename):
    pkl_file = open(filename, 'rb')
    res = cPickle.load(pkl_file)
    # print res
    pkl_file.close()
    return res
