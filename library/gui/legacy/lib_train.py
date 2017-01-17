# coding=utf-8
API_KEY = 'PBDGufho1Cvhb50Dkpy7YYCgCD3Uqs'
API_SECRET = 'COZgUqyVoChdLYjGAt6aZvc6VmOreO'


class FaceTrain(object):
    def __init__(self):
        self.api = API(API_KEY, API_SECRET)

    def open_group(self):
        result = self.api.info.get_group_list()['group']
        return result

    def _set_group_name(self, group_name):
        self.group_name = group_name

    def create_group(self, group_name):
        self.api.group.create(group_name=group_name)
        return group_name

    def add_person(self, person_name, group_name):
        self.api.person.create(person_name=person_name, group_name=group_name)
        return person_name

    def add_photo(self, person_name, images):
        count = 0
        for img in images:
            print img
            result = self.api.detection.detect(img=File(img), mode='oneface')
            face_id = result['face'][0]['face_id']
            self.api.person.add_face(person_name=person_name, face_id=face_id)
            count = count+1
        return count

    def train_face(self, person_name):
        sid = self.api.train.verify(person_name=person_name)
        return sid

    def delete_group(self, group_name):
        self.api.group.delete(group_name=group_name)
        return group_name

    def person_list(self):
        result = self.api.info.get_person_list()['person']
        return result

    def get_person_face(self, person_name):
        get_faces = self.api.person.get_info(person_name=person_name)['face']
        return get_faces

    def delete_photo_by_face_id(self, person_name, person_face_id):
        delete_result = self.api.person.remove_face(person_name=person_name, face_id=person_face_id)
        delete_num = delete_result['removed']
        delete_status = delete_result['success']
        print delete_status
        return delete_num

    def delete_person(self, person_name):
        self.api.person.delete(person_name=person_name)
        return person_name
