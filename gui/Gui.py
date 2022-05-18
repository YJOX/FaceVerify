import os
import shutil

import PySimpleGUI as sg

import Config
from database.Database import Database
from face.FaceRec import FaceRec
from utils import Log
from utils.FaceRecUtil import take_screenshot_from_video


class Gui(object):
    def __init__(self):
        sg.theme('DarkBlue')
        layout = [[sg.Text('Для начала вам нужно загрузить изображение с вашим лицом (анфас) в нашу базу данных.')],
                  [sg.Button('Загрузить')],
                  [sg.Text('Или сфотографируйте себя напрямую с вашей веб-камеры')],
                  [sg.Button('Сделать фото с камеры')],
                  [sg.Button('Начать обнаружение с камеры'), sg.Button('Отмена')]]

        window = sg.Window('FaceVerify', layout)
        while True:
            event, values = window.read()

            if event == sg.WIN_CLOSED or event == 'Отмена':
                break
            elif event == "Начать обнаружение с камеры":
                face_rec = FaceRec()
                face_rec.face_rec()
            elif event == "Сделать фото с камеры":
                take_screenshot_from_video()
            elif event == 'Загрузить':
                file = sg.popup_get_file('Пожалуйста, загрузите ваше изображение с лицом, где оно хорошо видно (анфас)',
                                         title='Изображение с лицом')
                print("file:" + file)
                if file:
                    name = sg.popup_get_text(
                        'Введите название лица (будет отображаться на камере при обнаружении данного лица)',
                        title='Название лица')
                    if name:
                        if Config.work_type == 1:
                            db = Database()
                            db.saveFaceEncoding(file, name)
                            db.close()
                        elif Config.work_type == 0:
                            shutil.copyfile(open(file.replace("file:", ""), "w+").read(), f"{Config.directory}/{name}.jpg") # Жесткий костыль, но работает
                        else:
                            Log.error("Неверный тип работы программы в конфиге")
                            return
                    sg.popup_cancel('Отменено - Вы отменили ввод названия изображения лица')
                else:
                    sg.popup_cancel('Отменено - Вы отменили загрузку изображения')

        window.close()
