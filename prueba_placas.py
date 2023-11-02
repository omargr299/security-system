import cv2
from clients.Detector.detectors import plates
from server.recognizers import plates as plates_rcg

cam = cv2.VideoCapture(1, cv2.CAP_DSHOW)

while True:
    ret, frame = cam.read()
    if not ret:
        break
    plate = plates.cut(frame)
    if plate is not None:
        cv2.imshow("plate", plate)
        text = plates_rcg.read(plate)
        print(text)
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break
