from facepp import *
import time
from pprint import pformat
import sys

import glob

# API_KEY = '38f0099662d8c2dad5615bfb79c70f26'
# API_SECRET = 'w2k7u1dU8xtPEXd9W3-IEdITK4HzvuVP'
API_KEY = 'PBDGufho1Cvhb50Dkpy7YYCgCD3Uqs'
API_SECRET = 'COZgUqyVoChdLYjGAt6aZvc6VmOreO'
# name_tr = "yanshuai"
name_tr = "liuhonghua"


def print_result(hint, result):
    def encode(obj):
        if type(obj) is unicode:
            return obj.encode('utf-8')
        if type(obj) is dict:
            return {encode(k): encode(v) for (k, v) in obj.iteritems()}
        if type(obj) is list:
            return [encode(i) for i in obj]
        return obj
    print hint
    result = encode(result)
    print '\n'.join(['  ' + i for i in pformat(result, width = 75).split('\n')])


api = API(API_KEY, API_SECRET)

#817 Liu honghua write begin
# api.group.create(group_name = 'vision')
# api.person.create(person_name =name_tr)
# api.person.create(person_name =name_tr, group_name = 'vision')
#api.group.add_person(name_tr)
# over

# imgs = glob.glob("yanshuai/*.png")
imgs = glob.glob("honghua/*.jpg")

# try:
#     # api.group.create(group_name = 'LTshenhua')
# api.person.create(person_name = name_tr, group_name = 'LTshenhua')
# except APIError as e:
#     print "Face++ error detected"
#     print "error code", e.code
#     sys.exit()

for img in imgs:
    print img
    result = api.detection.detect(img = File(img), mode = 'oneface')
    face_id = result['face'][0]['face_id']
    api.person.add_face(person_name = name_tr, face_id = face_id)

api.train.verify(person_name = name_tr)

# res2 = api.recognition.verify(person_name = "Jing Wei", face_id="3eaf483c7d754684efe53b045bd73d92")

# print res2

# print res2["is_same_person"]

# res = api.detection.detect(img = File('jw/3.jpg'))

# print_result('Train result:', res)