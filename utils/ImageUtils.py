import base64

import face_recognition


def toBase64(image_file): # Кодирование в Base64
    return base64.b64encode(image_file.read())

def fromBase64(b64): # Декодирование из Base64
    return b64.decode('base64')

def getCv2Encoding(rgb_img): # Получение кодировки изображения
    try:
        return face_recognition.face_encodings(rgb_img)[0]
    except IndexError as e:
        return None
