import abc
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from settings_parser import app_data

json_file_name: str = app_data.STATE_FILE_NAME
default_file_path: str = f"{Path(__file__).resolve().parent}"


class BaseStorage:
    @abc.abstractmethod
    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        pass

    @abc.abstractmethod
    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        pass


class JsonFileStorage(BaseStorage):
    def __init__(self, file_path: Optional[str] = None):
        self.file_path = file_path

    def save_state(self, state: dict) -> None:
        """Сохранить состояние в постоянное хранилище"""
        file_state = self.retrieve_state()
        with open(
            Path(self.file_path).joinpath(json_file_name), "w", encoding="utf-8"
        ) as storage:
            save_state: dict = {**file_state, **state}
            json.dump(save_state, storage, ensure_ascii=False, indent=4)

    def retrieve_state(self) -> dict:
        """Загрузить состояние локально из постоянного хранилища"""
        with open(
            Path(self.file_path).joinpath(json_file_name), "r", encoding="utf-8"
        ) as storage:
            return json.load(storage)


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не
    перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или
    распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state(state={key: value})

    def get_state(self, key: str) -> Any:
        """Получить состояние по определённому ключу"""
        return self.storage.retrieve_state().get(key) or datetime.min


my_state = State(storage=JsonFileStorage(file_path=default_file_path))
# my_state.set_state(key="person_updated_at", value="3")
# my_state.set_state(key="film_work_updated_at", value="2")
# my_state.set_state(key="genre_updated_at", value="1")
# print(my_state.get_state(key="person_updated_at"))
# print(my_state.get_state(key="film_work_updated_at"))
