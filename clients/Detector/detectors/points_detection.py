import os
import dlib
import cv2
import numpy as np


def get_rectangle(coordinates):
    x_st, y_st, x_end, y_end = coordinates.left(
    ), coordinates.top(), coordinates.right(), coordinates.bottom()
    return x_st, y_st, x_end, y_end


def get_point(frame, coordinate, point):
    shape = predictor(frame, coordinate)
    x, y = shape.part(point).x, shape.part(point).y
    return x, y


def get_points(frame, coordinate, ipoints=[i for i in range(68)]):
    shape = predictor(frame, coordinate)
    points = []
    for i in ipoints:
        x, y = shape.part(i).x, shape.part(i).y
        points.append((x, y))
    return np.array(points)


def normalize_points(points: list) -> np.ndarray:
    points = np.array(points, dtype=np.float32)
    center = points[30]
    points -= center
    # points /= np.linalg.norm(points, axis=0)
    return points


face_detector = dlib.get_frontal_face_detector()

dirname = os.path.dirname(os.path.realpath(__file__))
path = os.path.join(dirname, "assets", "shape_predictor_68_face_landmarks.dat")
if not os.path.exists(path):
    path = os.path.join(dirname, "..", "assets",
                        "shape_predictor_68_face_landmarks.dat")
predictor = dlib.shape_predictor(
    path)

if __name__ == '__main__':
    cap = cv2.VideoCapture(2)
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        coordinates = face_detector(gray, 1)
        for c in coordinates:
            rectangle = get_rectangle(c)
            cv2.rectangle(
                frame, (rectangle[0], rectangle[1]), (rectangle[2], rectangle[3]), (0, 255, 0), 2)
            points = get_points(gray, c)
            for p in points:
                cv2.circle(frame, p, 2, (255, 0, 0), 5)
        cv2.imshow("frame", frame)
        cv2.waitKey(1)
