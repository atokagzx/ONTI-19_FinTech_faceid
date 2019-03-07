import cognitive_face as cf
import cv2 as cv
import sys
import json

face_api_url = 'https://westcentralus.api.cognitive.microsoft.com/face/v1.0'
key_f = open('msfaceapi.json')
key_json = key_f.read()
KEY = json.loads(key_json)['key']
cf.Key.set(KEY)
cf.BaseUrl.set(face_api_url)
group_f = open('faceid.json')
group_json = group_f.read()
group_id = json.loads(group_json)['groupId']
try:
    cf.person_group.create(group_id)
except:
    pass

def get_person_id(p_name):
    persons = cf.person.lists(group_id)
    for i in persons:
        if i['name'] == p_name:
            return i['personId']
    return cf.person.create(group_id, p_name)['personId']

def get_person_name(p_id):
    persons = cf.person.lists(group_id)
    for i in persons:
        if i['personId'] == p_id:
            return i['name']

def delete(p_name):
    persons = cf.person.lists(group_id)
    for i in persons:
        if i['name'] == p_name:
            cf.person.delete(group_id, i['personId'])
            print("Person with id " +i['personId'] + " deleted")
            return 0
    raise Exception('No person with name "' + p_name + '"')

def train():
    cf.person_group.train(group_id)
    print("Training task for " + str(len(cf.person.lists(group_id))) + " persons started")

def add_person_pictures(person_id, file_path):
    cap = cv.VideoCapture(file_path)
    face_id = []
    if cap.get(7) < 5:
        raise Exception("Video does not contain any face")
    for i in range(5):
        cap.set(1, 0.25 * i)
        _, frame = cap.read()
        cv.imwrite(str(i) + '.png', frame)
        try:
            face_id.append(cf.person.add_face(str(i) + '.png', group_id, person_id))
        except:
            raise Exception("Video does not contain any face")
    print("5 frames extracted")
    print("PersonId: " + person_id)
    print("FaceIds")
    print("=======")
    for i in range(5):
        print(face_id[i]['persistedFaceId'])

def get_face_ids(file_path):
    face_id = []
    for i in range(5):
        cap = cv.VideoCapture(file_path)
        cap.set(1, 0.25 * i)
        _, frame = cap.read()
        cv.imwrite(str(i) + '.png', frame)
        detected_face = cf.face.detect(str(i) + '.png')
        if detected_face != []:
            face_id.append(detected_face[0]['faceId'])
        else:
            raise Exception("The person cannot be identified")
    return face_id

def detect(face_id):
    try:
        detect_list = cf.face.identify(face_id, group_id, threshold = 0.5)
    except:
        raise Exception("The system is not ready yet")
    try:
        ethalone = detect_list[0]['candidates'][0]['personId']
        for i in range(5):
            if ethalone != detect_list[i]['candidates'][0]['personId']:
                raise Exception("The person cannot be identified")
        print('The person is "' + get_person_name(ethalone) + '"')
    except:
        raise Exception("The person cannot be identified")
    
#person_id = get_person_id("Vlad")
#print(sys.argv)
if sys.argv[1] == "--name":
    person_id = get_person_id(sys.argv[2])
    add_person_pictures(person_id, '.\\' + sys.argv[3])
elif sys.argv[1] == "--del":
    delete(sys.argv[2])
elif sys.argv[1] == "--train":
    train()
elif sys.argv[1] == "--identify":
    detect(get_face_ids('.\\' + sys.argv[2]))
#delete("Elon Musk")
#add_persons_pictures(person_id, file_path)
#train()
#print(cf.person_group.get_status(group_id))
#print(cf.person.lists(group_id))
