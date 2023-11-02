import base64
import cv2
import numpy as np
import qrcode
from qrcode.image.styles.moduledrawers import SquareModuleDrawer
from qrcode.image.styledpil import StyledPilImage


def read_value(img: cv2.Mat):
    try:
        det = cv2.QRCodeDetector()
        valorQRLeido, pts, st_code = det.detectAndDecode(img)
        if valorQRLeido != "":

            return valorQRLeido

    except:
        pass
    # Mostramos el valor del QR leído
    return


def create(valorQR):
    # Preparamos el formato para el código QR
    QR = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    # imagenQR = os.path.dirname(os.path.abspath(__file__)) + '\codigo_qr.jpg'

    QR.add_data(valorQR)
    QR.make(fit=True)

    tipoQRC = SquareModuleDrawer()
    # Generamos el código QR y lo almacenamos en el fichero de imagen PNG
    img = QR.make_image(image_factory=StyledPilImage, module_drawer=tipoQRC)
    # convertimos la imagen a cv2 para poder trabajar con ella
    img = np.array(img.get_image())
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return img


def to_base64(img: cv2.Mat):
    img = cv2.imencode(".jpg", img)[1]
    img_base64 = base64.b64encode(img).decode("utf-8")
    return img_base64
