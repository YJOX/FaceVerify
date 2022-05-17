import glob
import json
import os
import PySimpleGUI as sg

import cv2
import face_recognition
import numpy
import numpy as np

import Config
from database.Database import Database
from utils import Log, ImageUtils


class FaceRecUtil:
    def __init__(self):
        self.known_face_encodings = []
        self.known_face_names = []

        # Изменяем размер фрейма для ускорения обработки изображения
        self.frame_resizing = 0.25

    def load_encoding_images(self):
        if Config.work_type == 0:
            images_path = glob.glob(os.path.join(Config.directory, "*.*"))
            images_len = len(images_path)

            if images_len == 0:
                Log.error(f"Не найдено изображений в директории {Config.directory}")
                return False

            Log.debug(f"{images_len} изображений найдено.")

            # Сохраняем кодировки изображения и его название из файлов
            for img_path in images_path:
                img = cv2.imread(img_path)
                rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

                # Получаем название файла изображения
                basename = os.path.basename(img_path)
                filename, ext = os.path.splitext(basename)

                # Получаем кодировку изображения из файлов
                try:
                    img_encoding = ImageUtils.getCv2Encoding(rgb_img)
                    # Сохраняем название и кодировку изображения в массив
                    self.known_face_encodings.append(img_encoding)
                    self.known_face_names.append(filename)
                except IndexError as e:
                    Log.error(f"На изображении {basename} не найдено лиц")
            Log.debug("Кодировки изображений загружены из файлов изображений")

        elif Config.work_type == 1:
            db = Database()  # Создаем подключение к БД
            for encoding_data in db.getFaceImages():  # Получаем все известные кодировки лиц из БД
                # Получаем кодировку изображения из бд
                try:
                    # Сохраняем название и кодировку изображения в массив
                    self.known_face_encodings.append(numpy.array(json.loads(encoding_data['encoding'])))
                    self.known_face_names.append(encoding_data['name'])
                except IndexError as e:
                    Log.error(f"Кодировка {encoding_data['name']} из БД неверная!")
            Log.debug("Кодировки изображений загружены из БД")
            db.close()
        else:
            Log.error("Неверный work_type в конфиге")
            return

    def detect_known_faces(self, frame):  # Обнаружение известного лица на кадре (frame)
        small_frame = cv2.resize(frame, (0, 0), fx=self.frame_resizing, fy=self.frame_resizing)
        rgb_small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(self.known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = self.known_face_names[best_match_index]
            face_names.append(name)

        face_locations = np.array(face_locations)
        face_locations = face_locations / self.frame_resizing
        return face_locations.astype(int), face_names


def take_screenshot_from_video():
    capture = cv2.VideoCapture(0)
    if not os.path.exists(Config.directory):
        os.mkdir(Config.directory)
    while True:
        ret, frame = capture.read()
        if ret:
            cv2.imshow("from camera", frame)
            cv2.putText(frame, "Для фото нажмите клавишу G", (10, 10), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 0, 0), 1)
            key = cv2.waitKey(30)
            if key == 27:  # escape
                break
            elif key == 103:  # Клавиша G
                name = sg.popup_get_text(
                    'Введите название лица (будет отображаться на камере при обнаружении данного лица)',
                    title='Название лица')
                if name:
                    jpg = f"{Config.directory}/{name}.jpg"
                    cv2.imwrite(jpg, frame) # Создаем файл jpg
                    if Config.work_type == 1: # Если у нас тип работы программы - БД
                        db = Database()
                        if db.saveFaceEncoding(jpg, name) is False: # Сохраняем кодировку лица из изображения в БД
                            Log.debug(f"На изображении {name} лиц не найдено")
                            db.close()
                            sg.popup_cancel(f'На изображении {name} лиц не найдено')
                            break
                        db.close()
                    Log.debug(f"Изображение {name} сделано успешно")
                    break
                else:
                    sg.popup_cancel('Отменено - Вы отменили ввод названия изображения лица')
        else:
            Log.error("Не удалось получить кадр из видео")
            break
    capture.release()
    cv2.destroyAllWindows()
