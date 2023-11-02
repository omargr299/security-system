
import cv2


def cut_qr(image: cv2.Mat):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.blur(gray, (3, 3))
    canny = cv2.Canny(gray, 150, 200)
    canny = cv2.dilate(canny, None, iterations=1)
    cnts, _ = cv2.findContours(
        canny, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)  # OpenCV 4
    # cv2.drawContours(image, cnts, -1, (0, 255, 0), 2)
    for c in cnts:
        area = cv2.contourArea(c)
        x, y, w, h = cv2.boundingRect(c)
        epsilon = 0.09*cv2.arcLength(c, True)
        approx = cv2.approxPolyDP(c, epsilon, True)
        if len(approx) == 4 and area > 5000:
            aspect_ratio = float(w)/h
            if aspect_ratio > 0.7 and aspect_ratio < 1.4:
                qr = image[y:y+h, x:x+w]
                cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 2)
                return qr
