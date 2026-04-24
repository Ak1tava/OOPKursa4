# -*- coding: utf-8 -*-
"""Модуль модели данных пароля.

Содержит класс PasswordModel — основную сущность приложения,
представляющую запись в менеджере паролей.
"""

import uuid
from dataclasses import dataclass, field, asdict
from typing import Dict, Any


@dataclass
class PasswordModel:
    """Класс-сущность для хранения информации о пароле.

    Представляет собой одну запись в менеджере паролей с полной
    информацией о сервисе, учётных данных и метаданных.

    Атрибуты:
        service_name (str): Название сервиса (например, «Google», «GitHub»).
        login (str): Логин или имя пользователя.
        password (str): Пароль в открытом виде (шифруется при сохранении).
        category (str): Категория записи (Соцсети, Учеба, Банки, Игры, Работа, Другое).
        linked_email (str): Привязанная электронная почта.
        is_favorite (bool): Флаг «Избранное» для быстрого доступа.
        id (str): Уникальный идентификатор записи (UUID4).
    """
    service_name: str
    login: str
    password: str
    category: str = "Другое"
    linked_email: str = ""
    is_favorite: bool = False
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация объекта в словарь для сохранения в JSON.

        Возвращает:
            Dict[str, Any]: Словарь со всеми полями модели.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PasswordModel":
        """Десериализация объекта из словаря.

        Фабричный метод для создания экземпляра PasswordModel
        из словаря, загруженного из JSON-файла.

        Аргументы:
            data (Dict[str, Any]): Словарь с данными записи.

        Возвращает:
            PasswordModel: Экземпляр модели пароля.
        """
        return cls(**data)

    def __str__(self) -> str:
        """Строковое представление записи (для отладки).

        Возвращает:
            str: Читаемое описание записи.
        """
        star = "★" if self.is_favorite else "☆"
        return (
            f"{star} [{self.category}] {self.service_name} "
            f"({self.login}) — {self.linked_email}"
        )
