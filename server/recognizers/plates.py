import pytesseract

pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract'


def read(plate):
    text = pytesseract.image_to_string(
        plate, config='--psm 7')  # obtener el texto de la placa
    # quitar espacios en blanco y limitar el texto a 9 caracteres
    text = text.replace(' ', '')
    print(text)
    if len(text) < 9:
        return None
    text = text[:9]
    if text == '':
        return None

    return text
