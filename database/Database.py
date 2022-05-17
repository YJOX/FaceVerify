import json

import cv2
import pymysql
from pymysql.cursors import DictCursor

import Config
from utils import ImageUtils, Log


class Database(object):  # Класс, отвечающий за работу с БД
    def __init__(self):
        (self.connection) = pymysql.connect(
            host=Config.host,
            port=Config.port,
            user=Config.username,
            password=Config.password,
            db=Config.database,
            charset='utf8mb4',
            cursorclass=DictCursor
        )
        self.initDatabase()

    def initDatabase(self):
        # with self.connection.cursor() as cursor:
        #     query = "create database IF NOT EXISTS face_verify"  # Создание БД если ее не существует
        #     cursor.execute(query) # TODO Почему-то не работает
        with self.connection.cursor() as cursor:
            query = """
                    CREATE TABLE IF NOT EXISTS faces
                    (ID INT NOT NULL AUTO_INCREMENT,
                    name VARCHAR(64) NOT NULL,
                    encoding TEXT NOT NULL,
                    PRIMARY KEY (ID))
                """
            cursor.execute(query)
        self.connection.commit()

    def getFaceImages(self):  # Получение всех кодировок изображений лиц из БД
        with self.connection.cursor() as cursor:
            query = "SELECT * FROM faces"
            cursor.execute(query)
            return cursor

    def saveFaceEncoding(self, file, name):  # Сохранение кодировки лица с изображения в БД
        with self.connection.cursor() as cursor:
            img = cv2.imread(file)
            rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            encoding = ImageUtils.getCv2Encoding(rgb_img)
            if encoding is None:
                encoding = json.dumps(encoding.tolist())
                return False
            query = f"""
                INSERT INTO faces (name, encoding) VALUES ('{name}', '{encoding}')
                """
            Log.debug("query" + query)
            cursor.execute(query)
            self.connection.commit()

    def close(self):
        self.connection.close()
