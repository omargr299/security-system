
import cv2

import detectors.points_detection as ptd

MARGIN = 30
LIMIT = 20


def getFaces(frame: cv2.Mat):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    coordinates = ptd.face_detector(gray, 1)
    faces = []
    for c in coordinates:
        face = gray[c.top():c.bottom(), c.left():c.right()]
        face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_CUBIC)
        # cv2.rectangle(
        # frame, (c.left(), c.top()), (c.right(), c.bottom()), (0, 255, 0), 2)
        faces.append({"face": face, "rectangle": c})

    return faces
