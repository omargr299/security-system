
import cv2
import registers.points_detection as ptd


MARGIN = 30
LIMIT = 20


def isCenter(center: int, top: int, bottom: int, middlex: int = 0, middley: int = 0) -> bool:
    if center is None or top is None or bottom is None:
        return False

    if center[0] < middley-MARGIN or center[0] > middley+MARGIN or center[1] < middlex-MARGIN or center[1] > middlex+MARGIN:
        return False

    if top[0] < center[0]-MARGIN or top[0] > center[0]+MARGIN:
        return False

    if bottom[0] < center[0]-MARGIN or bottom[0] > center[0]+MARGIN:
        return False

    return True


def getFaces(frame: cv2.Mat):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    coordinates = ptd.face_detector(gray, 1)
    faces = []
    for c in coordinates:
        face = gray[c.top():c.bottom(), c.left():c.right()]
        face = cv2.resize(face, (160, 160), interpolation=cv2.INTER_CUBIC)
        cv2.rectangle(
            frame, (c.left(), c.top()), (c.right(), c.bottom()), (0, 255, 0), 2)
        faces.append({"face": face, "rectangle": c})

    return faces


def capture(frame: cv2.Mat, faceSamples: list):

    faces = getFaces(frame)

    width, heigth, _ = frame.shape
    middlex, middley = width//2, heigth//2

    for face in faces:
        rectangle = face["rectangle"]

        cv2.circle(frame, (middley, middlex), 2, (100, 200, 0), 5)

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        center, top, bottom = ptd.get_points(gray, rectangle, [
            30, 27, 8])

        cv2.circle(frame, center, 2, (100, 200, 0), 5)
        cv2.circle(frame, top, 2, (255, 0, 0), 5)
        cv2.circle(frame, bottom, 2, (255, 0, 0), 5)

        cv2.putText(frame, str(len(faceSamples)), (80, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 2)

        if not isCenter(center, top, bottom, middlex, middley):
            continue

        faceSamples.append(face["face"])
