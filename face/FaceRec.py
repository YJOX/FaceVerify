from threading import Thread

import cv2

from utils import Log
from utils.FaceRecUtil import FaceRecUtil

class FaceRec(object):
    def __init__(self):
        (self.capture) = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.capture.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        W, H = 640, 480
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, W)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, H)
        self.capture.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
        self.capture.set(cv2.CAP_PROP_FPS, 30)
        (self.thread) = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

    def update(self):
        while True:
            if self.capture.isOpened():
                (self.ret, self.frame) = self.capture.read()

    def face_rec(self):
        sfr = FaceRecUtil()
        if sfr.load_encoding_images() is False:
            return

        while True:
            try:
                # Обнаружение лиц
                face_locations, face_names = sfr.detect_known_faces(self.frame)
                for face_loc, name in zip(face_locations, face_names):
                    # print(face_loc)
                    y1, x1, y2, x2 = face_loc[0], face_loc[1], face_loc[2], face_loc[
                        3]  # Координаты лица на видео (с камеры)

                    cv2.putText(self.frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 2)
                    cv2.rectangle(self.frame, (x1, y1), (x2, y2), (0, 0, 200), 2)

                if self.ret:
                    cv2.imshow("Frame", self.frame)
                    key = cv2.waitKey(30)
                    if key == 27:  # escape (выход из окна с отображением камеры)
                        break
                else:
                    Log.error("Не удалось получить кадр из видео")
                    break
            except AttributeError:
                pass
        self.capture.release()
        cv2.destroyAllWindows()
