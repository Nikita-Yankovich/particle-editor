import json
import pygame
import os
from Emitter import Emitter

class SceneManager:
    def __init__(self):
        self.emitters = [] # Список, где хранятся активные эмиттеры сцены, в порядке их слоёв!

    def load_scene(self, file_path): # Загрузка сцены из JSON-файла сохранений
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.emitters.clear()

            json_dir = os.path.dirname(os.path.abspath(file_path))
            
            # enumerate автоматически дает индекс элемента (0, 1, 2...), который мы используем как послойный emitter_id!
            for current_layer, emitter_data in enumerate(data):
                # Пространственные характеристики + config эмиттера
                pos = (emitter_data['posX'], emitter_data['posY'])
                rotation = emitter_data.get('rotation', 0)
                scale = emitter_data.get('scale', 1.0)
                config = emitter_data['config']
                # Color parcing (saves and loads from json as String!)
                if isinstance(config['start_rgba'], str):
                    config['start_rgba'] = [int(c) for c in config['start_rgba'].split(',')]
                if isinstance(config['end_rgba'], str):
                    config['end_rgba'] = [int(c) for c in config['end_rgba'].split(',')]

                # Передаём путь к файлу конфигурации в config
                config['json_dir'] = json_dir
                
                # Создаем объект эмиттера, передавая ему слой в качестве ID
                new_emitter = Emitter(pos, rotation, scale, current_layer, config)
                # Добавляем эмиттер в данный SceneManager
                self.emitters.append(new_emitter)
                
            print(f"Успешно загружена сцена: {file_path}. Создано эмиттеров: {len(self.emitters)}")
            
        except FileNotFoundError:
            print(f"Ошибка: Файл {file_path} не найден.")
        except Exception as e:
            print(f"Ошибка при парсинге файла сцены: {e}")

    def update(self, dt):
        for emitter in self.emitters:
            emitter.update(dt)

    def draw(self, surface, camPos):
        surface.fill((0, 0, 0))
        # Рисуем эмиттеры строго в том порядке, в котором они шли в JSON-файле
        for emitter in self.emitters:
            emitter.draw(surface, camPos)
