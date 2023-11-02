import base64
import numpy as np
import os
import cv2
import recognizers.model as mdl

recognizer = mdl.FaceRecognizer()


def recognize(face: cv2.Mat):

    label = recognizer.predict(face)

    return label


LIMIT = 10


def regist(faces: list, label: str or int, skip: bool = False):

    faces = list(map(lambda face: base64.b64decode(face), faces))
    faces = list(map(lambda face: np.frombuffer(face, np.uint8), faces))
    faces = list(map(lambda face: cv2.imdecode(
        face, flags=cv2.IMREAD_COLOR), faces))
    faces = list(map(lambda face: cv2.cvtColor(
        face, cv2.COLOR_BGR2GRAY), faces))
    label = int(label)
    registedFaces, registedLabels = mdl.getRegisted(
    ) if not skip else mdl.getRegisted([label])

    labels = [label] * len(faces)

    faces.extend(registedFaces)
    labels.extend(registedLabels)

    recognizer.train(faces, labels)
    mdl.regist(faces[:LIMIT], label)


def unRegist(label: str or int):
    label = int(label)
    total = mdl.unRegist(label)
    if total == 0:
        recognizer.deleteModel()
        return
    registedFaces, registedLabels = mdl.getRegisted()
    if len(registedFaces) == 0:
        recognizer.deleteModel()
        return
    recognizer.train(registedFaces, registedLabels)
