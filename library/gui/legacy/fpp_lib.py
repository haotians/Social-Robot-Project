# export PYTHONPATH=$PYTHONPATH:/home/ewayGit
API_KEY = 'PBDGufho1Cvhb50Dkpy7YYCgCD3Uqs'
API_SECRET = 'COZgUqyVoChdLYjGAt6aZvc6VmOreO'
NAME_DB = ["JW", "T. Bowei", "X. Jiayi", "L. Honghua"]


class FaceppLib(object):
    """
        a wrapper class, start connection at the beginning to init the session
    """
    def __init__(self):
        self.api = API(API_KEY, API_SECRET)

    def verify(self, img_file=None):
        if img_file is None:
            return None, None

        result = self.api.detection.detect(img=File(img_file), mode='oneface')
        print result
        face_id = result['face'][0]['face_id']

        for name in NAME_DB:
            res2 = self.api.recognition.verify(person_name=name, face_id=face_id)
            print res2
            if res2["is_same_person"] is True:
                return name, result
        if res2["is_same_person"] is False:
            return None, result

    def verify_multiple_people(self, img_file=None):
        if img_file is None:
            return None, None
        result = self.api.detection.detect(img=File(img_file), mode='normal')
        faceId = []
        for i in range(0, len(result['face'])):
            faceId.append(result['face'][i]['face_id'])
        res2 = []
        recognizeName = []
        j = 0
        # recognize every faceId to get the name of the face
        for i in range(0, len(faceId)):
            for name in NAME_DB:
                res2.append(self.api.recognition.verify(person_name=name, face_id=faceId[i]))
                if res2[j]["is_same_person"] is True:
                    recognizeName.append(name)
                    j = j + 1
                    # print name
                    break

                j = j + 1
            if res2[j-1]["is_same_person"] is False:
                recognizeName.append("not in db")
                # print "not in db"
        return recognizeName, result

if __name__ == '__main__':
    # res = face_verify(img_file="temp.jpg")
    face = FaceppLib()
    face.verify(img_file="temp.jpg")
