import os
import pickle
import sys

import face_recognition

import Config
from utils import Log


def train_model_by_img(name): # Тренировка модели (программы, ИИ) по изображениям (временно не работает и не используется)
    if not os.path.exists("dataset"):
        Log.error("Директории \"dataset\" не существует")
        sys.exit()

    known_encodings = []
    images = os.listdir("dataset")

    for (i, image) in enumerate(images):
        Log.debug(f"Processing img {i + 1}/{len(images)}")

        face_img = face_recognition.load_image_file(f"{Config.directory}/{image}")
        face_enc = face_recognition.face_encodings(face_img)[0]

        known_encodings_len = len(known_encodings)
        if known_encodings_len == 0:
            known_encodings.append(face_enc)
        else:
            for item in range(0, known_encodings_len):
                result = face_recognition.compare_faces([face_enc], known_encodings[item])
                Log.debug(f"result - {result}")

                if result[0]:
                    known_encodings.append(face_enc)
                    Log.info("Лицо найдено в БД")
                    break
                Log.warning("Лицо не найдено в БД")
                break

    data = {
        "name": name,
        "encodings": known_encodings
    }

    with open(f"{name}_encoding.pickle", "wb") as file:
        file.write(pickle.dumps(data))

    return Log.info(f"Файл {name}_encoding.pickle успешно создан")