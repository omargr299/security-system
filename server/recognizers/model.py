
import os
import re
import cv2
import numpy as np


class FaceRecognizer:

    def __init__(self) -> None:
        self.recog = cv2.face.LBPHFaceRecognizer_create()
        dirname = os.path.dirname(os.path.realpath(__file__))
        self.path = os.path.join(dirname, 'face_recog.xml')
        self.isLoaded = False
        if os.path.exists(self.path):
            self.recog.read(self.path)
            self.isLoaded = True

    def train(self, faces: np.ndarray, labels: list):
        self.recog.train(faces, np.array(labels))
        label = labels[0]
        self.save()

    def predict(self, face: np.ndarray):
        if not self.isLoaded:
            return -1
        face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_CUBIC)
        predict = self.recog.predict(face)
        if predict[1] > 50:
            return -1

        return predict[1]

    def save(self):
        self.recog.save(self.path)

    def deleteModel(self):
        if os.path.exists(self.path):
            os.remove(self.path)


def getRegisted(exceptions: list[int] = [-1]):
    faces = []
    labels = []

    dirname = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dirname, 'regists')

    total = 0
    folders = os.listdir(path) if os.path.exists(path) else []
    exceptions = [str(i) for i in exceptions]
    for folder in folders:
        total += 1
        if folder in exceptions:
            continue

        for file in os.listdir(os.path.join(path, folder)):
            face = cv2.imread(path+folder+"/"+file)
            if face is None:
                continue
            face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_CUBIC)
            face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
            faces.append(face)
            labels.append(int(folder))

    return faces, labels


def regist(faces, label):
    dirname = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dirname, 'regists')

    if not os.path.exists(path):
        os.mkdir(path)
    registPath = os.path.join(path, str(label))
    extention = ".jpg"

    if not os.path.exists(registPath):
        os.mkdir(registPath)

    for i, face in enumerate(faces):
        with open(os.path.join(registPath, str(i)+extention), "wb") as file:
            file.write(cv2.imencode(extention, face)[1])


def unRegist(label):
    dirname = os.path.dirname(os.path.realpath(__file__))
    path = os.path.join(dirname, 'regists')

    if not os.path.exists(path):
        return

    registPath = os.path.join(path, str(label))

    if not os.path.exists(registPath):
        return

    for file in os.listdir(registPath):
        os.remove(os.path.join(registPath, file))

    os.rmdir(registPath)

    return len(os.listdir(path))
