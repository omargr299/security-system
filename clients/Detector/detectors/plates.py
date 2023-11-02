import cv2
from numpy import ndarray


def cut(image: ndarray):

    placa = []
    umbral = 80

    copy = image.copy()
    gray = cv2.cvtColor(copy, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, (3, 3))
    canny = cv2.Canny(gray, 50, 200)
    canny = cv2.dilate(canny, None, iterations=1)

    cnts, _ = cv2.findContours(canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)

    for c in cnts:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        epsilon = 0.09*cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)

        if len(approx) >= 2 and area > 15000:

            cv2.drawContours(copy, [approx], 0, (0, 255, 0), 3)

            aspect_ratio = float(w)/h

            if aspect_ratio > 2 and aspect_ratio < 3:
                placa = gray[y:y+h, x:x+w]
                placa = cv2.resize(placa, (200, 100))

                placa = placa[20:95, :]
                # binarizar la placa
                placa[placa >= umbral] = 255
                placa[placa < umbral] = 0

                # dibujar el rectangulo de la placa
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 3)

                return placa
