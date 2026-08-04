import json
# import pygame
import os
import ctypes
from Emitter import Emitter


class SceneManager:
    SUCCESS = 'success'
    FAILED = 'failed'
    ASK_REQUIRED = 'ask_required'

    def __init__(self):
        self.emitters = []  # Список, где хранятся активные эмиттеры сцены, в порядке их слоёв!
        self.original_scene_path = None  # Исходный файл сохранения. До явного сохранения не изменяется.
        self.working_scene_path = None  # Временная рабочая копия открытой сцены.

    def open_scene(self, file_path, safety_mode='ask'):
        """
        Открывает сцену через её временную рабочую копию.

        ask:
            создаёт рабочий файл, если его нет;
            требует решения пользователя, если файл уже существует.

        hard:
            перезаписывает рабочий файл данными постоянной сцены.

        soft:
            открывает существующий рабочий файл без перезаписи.
        """

        if safety_mode not in {'ask', 'hard', 'soft'}:
            print(f"Unsupported open safety_mode: {safety_mode}")
            return self.FAILED

        original_path = os.path.abspath(file_path)
        original_directory = os.path.dirname(original_path)
        original_filename = os.path.basename(original_path)
        scene_name = os.path.splitext(original_filename)[0]

        working_path = os.path.join(
            original_directory,
            f".{scene_name}.working.json"
        )

        working_file_exists = os.path.isfile(working_path)

        # Пока UI отсутствует, контроллер получает статус
        # и самостоятельно решает, вызвать hard или soft.
        if safety_mode == 'ask' and working_file_exists:
            return self.ASK_REQUIRED

        # Soft открывает только уже существующую рабочую копию.
        if safety_mode == 'soft':
            if not working_file_exists:
                print(f"Working scene file not found: {working_path}")
                return self.FAILED

            if not self.load_scene(working_path):
                return self.FAILED

            return self.SUCCESS

        # Сюда попадают:
        # - hard;
        # - ask, если рабочей копии ещё нет.
        if not os.path.isfile(original_path):
            print(f"Scene file not found: {original_path}")
            return self.FAILED

        try:
            with open(
                    original_path,
                    'r',
                    encoding='utf-8'
            ) as original_file:
                original_data = json.load(original_file)

            if not isinstance(original_data, list):
                raise ValueError(
                    "Source scene must contain a list of scene objects."
                )

            scene_objects = []

            for scene_object in original_data:
                if not isinstance(scene_object, dict):
                    raise ValueError(
                        "Every scene object must be a JSON object."
                    )

                copied_object = scene_object.copy()

                # Для обратной совместимости старые объекты
                # без type считаются эмиттерами.
                object_type = copied_object.setdefault(
                    'type',
                    'emitter'
                )

                if object_type == '_working_state':
                    raise ValueError(
                        "Source scene contains a working-state object."
                    )

                scene_objects.append(copied_object)

            working_data = [
                {
                    'type': '_working_state',
                    'source_scene': original_path,
                    'is_saved': True
                },
                *scene_objects
            ]

            # Режим hard сознательно перезаписывает
            # предыдущую рабочую копию.
            with open(
                    working_path,
                    'w',
                    encoding='utf-8'
            ) as working_file:
                json.dump(
                    working_data,
                    working_file,
                    ensure_ascii=False,
                    indent=4
                )

            if os.name == 'nt':
                attributes = (
                    ctypes.windll.kernel32.GetFileAttributesW(
                        working_path
                    )
                )

                if attributes != -1:
                    ctypes.windll.kernel32.SetFileAttributesW(
                        working_path,
                        attributes | 0x02
                    )

            if not self.load_scene(working_path):
                self._delete_working_file(working_path)
                return self.FAILED

            return self.SUCCESS

        except Exception as error:
            print(f"Failed to open scene: {error}")
            return self.FAILED

    def load_scene(self, file_path):  # Загружает runtime-сцену из указанного JSON-файла.
        """
        Загружает runtime-сцену из временного JSON-файла.

        Обычные постоянные сохранения этот метод напрямую
        читать не должен.
        """

        try:
            with open(
                    file_path,
                    'r',
                    encoding='utf-8'
            ) as file:
                data = json.load(file)

            if not isinstance(data, list):
                raise ValueError(
                    "Working scene must contain a list of objects."
                )

            working_states = [
                scene_object
                for scene_object in data
                if isinstance(scene_object, dict)
                   and scene_object.get('type') == '_working_state'
            ]

            # Рабочее состояние должно присутствовать ровно один раз.
            if len(working_states) != 1:
                raise ValueError(
                    "Working scene must contain exactly one "
                    "'_working_state' object."
                )

            working_state = working_states[0]

            # У служебного объекта допускаются только эти поля.
            if set(working_state.keys()) != {
                'type',
                'source_scene',
                'is_saved'
            }:
                raise ValueError(
                    "Invalid '_working_state' structure."
                )

            if not isinstance(
                    working_state['source_scene'],
                    str
            ):
                raise ValueError(
                    "'source_scene' must be a string."
                )

            if not isinstance(
                    working_state['is_saved'],
                    bool
            ):
                raise ValueError(
                    "'is_saved' must be a boolean."
                )

            json_dir = os.path.dirname(
                os.path.abspath(file_path)
            )

            new_emitters = []

            for scene_object in data:
                # Служебный объект не является объектом сцены.
                if scene_object is working_state:
                    continue

                if not isinstance(scene_object, dict):
                    raise ValueError(
                        "Every scene object must be a JSON object."
                    )

                # Обратная совместимость со старыми сценами.
                object_type = scene_object.get(
                    'type',
                    'emitter'
                )

                if object_type == 'emitter':
                    emitter_data = scene_object

                    pos = (
                        emitter_data['posX'],
                        emitter_data['posY']
                    )

                    rotation = emitter_data.get(
                        'rotation',
                        0
                    )

                    scale = emitter_data.get(
                        'scale',
                        1.0
                    )

                    # Копируем конфигуратор, чтобы json_dir
                    # не попал в прочитанные данные.
                    config = emitter_data['config'].copy()

                    if isinstance(config['start_rgba'], str):
                        config['start_rgba'] = [
                            int(component)
                            for component
                            in config['start_rgba'].split(',')
                        ]

                    if isinstance(config['end_rgba'], str):
                        config['end_rgba'] = [
                            int(component)
                            for component
                            in config['end_rgba'].split(',')
                        ]

                    config['json_dir'] = json_dir

                    # Служебное состояние и будущие триггеры
                    # не должны влиять на индексацию эмиттеров.
                    emitter_id = len(new_emitters)

                    new_emitter = Emitter(
                        pos,
                        rotation,
                        scale,
                        emitter_id,
                        config
                    )

                    new_emitters.append(new_emitter)

                elif object_type == 'trigger':
                    raise NotImplementedError(
                        "Trigger objects are not supported yet."
                    )

                else:
                    raise ValueError(
                        f"Unsupported scene object type: {object_type}"
                    )

            # Текущая runtime-сцена заменяется только после
            # успешной обработки всего рабочего файла.
            self.emitters = new_emitters

            self.original_scene_path = os.path.abspath(
                working_state['source_scene']
            )

            self.working_scene_path = os.path.abspath(
                file_path
            )

            print(
                f"Scene loaded successfully: {file_path}. "
                f"Emitters created: {len(self.emitters)}"
            )

            return True

        except FileNotFoundError:
            print(f"Scene file not found: {file_path}")
            return False

        except Exception as error:
            print(f"Failed to load scene: {error}")
            return False

    def close_scene(self, safety_mode='ask'):
        """
        Закрывает текущую сцену.

        ask:
            удаляет сохранённую рабочую копию;
            требует решения пользователя для несохранённой.

        hard:
            удаляет рабочую копию независимо от is_saved.

        soft:
            закрывает сцену, оставляя рабочую копию.
        """

        if safety_mode not in {'ask', 'hard', 'soft'}:
            print(f"Unsupported close safety_mode: {safety_mode}")
            return self.FAILED

        if self.working_scene_path is None:
            print("No scene is currently open.")
            return self.FAILED

        if safety_mode == 'ask':
            try:
                with open(
                        self.working_scene_path,
                        'r',
                        encoding='utf-8'
                ) as working_file:
                    data = json.load(working_file)

                if not isinstance(data, list):
                    raise ValueError(
                        "Working scene must contain a list of objects."
                    )

                working_states = [
                    scene_object
                    for scene_object in data
                    if isinstance(scene_object, dict)
                       and scene_object.get('type') == '_working_state'
                ]

                if len(working_states) != 1:
                    raise ValueError(
                        "Working scene must contain exactly one "
                        "'_working_state' object."
                    )

                is_saved = working_states[0].get('is_saved')

                if not isinstance(is_saved, bool):
                    raise ValueError(
                        "'is_saved' must be a boolean."
                    )

                # Сохранённый рабочий файл при штатном
                # закрытии больше не нужен.
                if is_saved:
                    safety_mode = 'hard'
                else:
                    return self.ASK_REQUIRED

            except Exception as error:
                print(f"Failed to close scene: {error}")
                return self.FAILED

        if safety_mode == 'hard':
            if not self._delete_working_file(
                    self.working_scene_path
            ):
                return self.FAILED

        elif safety_mode == 'soft':
            if not os.path.isfile(self.working_scene_path):
                print(
                    "Working scene cannot be preserved because "
                    "its file does not exist."
                )
                return self.FAILED

        # И hard, и soft закрывают runtime-сцену.
        # Отличается только судьба рабочего файла.
        self.original_scene_path = None
        self.working_scene_path = None
        self.emitters.clear()

        return self.SUCCESS

    @staticmethod
    def _delete_working_file(file_path):  # Применяется ситуативно по правилам Схемы системы доступа к данным (см. docs)
        """Удаляет временный файл по указанному пути."""

        if file_path is None:
            return True

        if not os.path.isfile(file_path):
            return True

        try:
            os.remove(file_path)
            return True

        except OSError as error:
            print(
                f"Failed to delete temporary file "
                f"{file_path}: {error}"
            )
            return False

    def update(self, dt):
        for emitter in self.emitters:
            emitter.update(dt)

    def draw(self, surface, camPos):
        surface.fill((0, 0, 0))
        # Рисуем эмиттеры строго в том порядке, в котором они шли в JSON-файле
        for emitter in self.emitters:
            emitter.draw(surface, camPos)
