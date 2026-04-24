# -*- coding: utf-8 -*-
"""Модуль работы с базой данных (хранилищем паролей).

Содержит класс DatabaseEngine, обеспечивающий все CRUD-операции
над зашифрованной JSON-базой данных: создание хранилища, загрузку,
добавление/обновление/удаление записей, поиск и фильтрацию.
"""

import json
import os
import base64
from typing import List, Optional

from models.password_model import PasswordModel
from core.encryption import EncryptionManager


class DatabaseEngine:
    """Движок базы данных для управления зашифрованным хранилищем паролей.

    Реализует паттерн «Репозиторий» для записей паролей.
    Данные хранятся в JSON-файле в следующей структуре:
    {
        "salt": "<base64-соль для PBKDF2>",
        "data": "<Fernet-токен с зашифрованным массивом записей>"
    }

    При каждой модификации данных файл перезаписывается атомарно.

    Атрибуты:
        _encryption (EncryptionManager): Менеджер шифрования.
        _db_path (str): Путь к файлу базы данных.
        _entries (List[PasswordModel]): Список записей в памяти.
    """

    def __init__(self, encryption_manager: EncryptionManager, db_path: str = "vault.dat"):
        """Инициализация движка базы данных.

        Аргументы:
            encryption_manager (EncryptionManager): Экземпляр менеджера шифрования.
            db_path (str): Путь к файлу базы данных. По умолчанию «vault.dat».
        """
        self._encryption = encryption_manager
        self._db_path = db_path
        self._entries: List[PasswordModel] = []

    # ==================== Управление хранилищем ====================

    def vault_exists(self) -> bool:
        """Проверка существования файла хранилища.

        Возвращает:
            bool: True, если файл базы данных существует на диске.
        """
        return os.path.exists(self._db_path)

    def create_vault(self, master_password: str) -> None:
        """Создание нового зашифрованного хранилища.

        Генерирует соль, выводит ключ из мастер-пароля и сохраняет
        пустую базу данных в зашифрованном виде.

        Аргументы:
            master_password (str): Мастер-пароль для нового хранилища.

        Исключения:
            ValueError: Если мастер-пароль пуст.
            IOError: Если не удалось записать файл.
        """
        salt = self._encryption.generate_salt()
        self._encryption.derive_key(master_password, salt)
        self._entries = []
        self._save()

    def unlock_vault(self, master_password: str) -> bool:
        """Разблокировка существующего хранилища мастер-паролем.

        Читает файл базы данных, извлекает соль, выводит ключ
        из мастер-пароля и пытается расшифровать данные.
        При неверном пароле возвращает False.

        Аргументы:
            master_password (str): Мастер-пароль для разблокировки.

        Возвращает:
            bool: True при успешной разблокировке, False при неверном пароле.
        """
        try:
            with open(self._db_path, "r", encoding="utf-8") as f:
                vault_data = json.load(f)

            # Извлечение соли и вывод ключа
            salt = base64.b64decode(vault_data["salt"])
            self._encryption.derive_key(master_password, salt)

            # Дешифрование массива записей
            encrypted_data = vault_data["data"]
            decrypted_json = self._encryption.decrypt_data(encrypted_data)
            entries_list = json.loads(decrypted_json)

            # Десериализация записей
            self._entries = [PasswordModel.from_dict(entry) for entry in entries_list]
            return True

        except Exception:
            # Неверный пароль или повреждённый файл
            self._entries = []
            return False

    # ==================== CRUD-операции ====================

    def add_entry(self, entry: PasswordModel) -> None:
        """Добавление новой записи в хранилище.

        Аргументы:
            entry (PasswordModel): Новая запись для добавления.
        """
        self._entries.append(entry)
        self._save()

    def update_entry(self, entry_id: str, updated_entry: PasswordModel) -> bool:
        """Обновление существующей записи по идентификатору.

        Аргументы:
            entry_id (str): UUID записи для обновления.
            updated_entry (PasswordModel): Обновлённая запись.

        Возвращает:
            bool: True, если запись найдена и обновлена.
        """
        for i, entry in enumerate(self._entries):
            if entry.id == entry_id:
                updated_entry.id = entry_id  # Сохранение исходного ID
                self._entries[i] = updated_entry
                self._save()
                return True
        return False

    def delete_entry(self, entry_id: str) -> bool:
        """Удаление записи по идентификатору.

        Аргументы:
            entry_id (str): UUID записи для удаления.

        Возвращает:
            bool: True, если запись была найдена и удалена.
        """
        original_count = len(self._entries)
        self._entries = [e for e in self._entries if e.id != entry_id]
        if len(self._entries) < original_count:
            self._save()
            return True
        return False

    def toggle_favorite(self, entry_id: str) -> Optional[bool]:
        """Переключение статуса «Избранное» для записи.

        Аргументы:
            entry_id (str): UUID записи.

        Возвращает:
            Optional[bool]: Новое значение is_favorite, или None если не найдена.
        """
        for entry in self._entries:
            if entry.id == entry_id:
                entry.is_favorite = not entry.is_favorite
                self._save()
                return entry.is_favorite
        return None

    # ==================== Получение данных ====================

    def get_all_entries(self) -> List[PasswordModel]:
        """Получение всех записей из хранилища.

        Возвращает:
            List[PasswordModel]: Копия списка всех записей.
        """
        return self._entries.copy()

    def get_entry_by_id(self, entry_id: str) -> Optional[PasswordModel]:
        """Поиск записи по идентификатору.

        Аргументы:
            entry_id (str): UUID записи.

        Возвращает:
            Optional[PasswordModel]: Запись или None, если не найдена.
        """
        for entry in self._entries:
            if entry.id == entry_id:
                return entry
        return None

    # ==================== Поиск и фильтрация ====================

    def search_by_service(self, query: str) -> List[PasswordModel]:
        """Поиск записей по названию сервиса (нечувствительный к регистру).

        Аргументы:
            query (str): Поисковый запрос (подстрока).

        Возвращает:
            List[PasswordModel]: Список записей, содержащих запрос в названии.
        """
        if not query:
            return self._entries.copy()
        query_lower = query.lower()
        return [
            e for e in self._entries
            if query_lower in e.service_name.lower()
            or query_lower in e.login.lower()
        ]

    def filter_by_email(self, email: str) -> List[PasswordModel]:
        """Фильтрация записей по привязанной электронной почте.

        Аргументы:
            email (str): Адрес электронной почты для фильтрации.
                         Пустая строка или «Все почты» — без фильтрации.

        Возвращает:
            List[PasswordModel]: Список записей с указанной почтой.
        """
        if not email or email == "Все почты":
            return self._entries.copy()
        return [e for e in self._entries if e.linked_email == email]

    def filter_by_category(self, category: str) -> List[PasswordModel]:
        """Фильтрация записей по категории.

        Аргументы:
            category (str): Название категории (Соцсети, Учеба и т.д.).

        Возвращает:
            List[PasswordModel]: Список записей указанной категории.
        """
        return [e for e in self._entries if e.category == category]

    def get_favorites(self) -> List[PasswordModel]:
        """Получение всех избранных записей.

        Возвращает:
            List[PasswordModel]: Список записей с флагом is_favorite=True.
        """
        return [e for e in self._entries if e.is_favorite]

    def get_unique_emails(self) -> List[str]:
        """Получение списка уникальных привязанных почтовых ящиков.

        Используется для наполнения выпадающего списка (ComboBox)
        в интерфейсе.

        Возвращает:
            List[str]: Отсортированный список уникальных email-адресов.
        """
        emails = set()
        for entry in self._entries:
            if entry.linked_email:
                emails.add(entry.linked_email)
        return sorted(emails)

    def get_entry_count(self) -> int:
        """Получение общего числа записей в хранилище.

        Возвращает:
            int: Количество записей.
        """
        return len(self._entries)

    # ==================== Внутренние методы ====================

    def _save(self) -> None:
        """Сохранение текущего состояния базы данных в зашифрованный файл.

        Сериализует все записи в JSON, шифрует полученную строку
        алгоритмом Fernet и записывает в файл вместе с солью.

        Исключения:
            RuntimeError: Если ключ шифрования не инициализирован.
            IOError: Если не удалось записать файл.
        """
        try:
            # Сериализация записей в JSON-строку
            entries_json = json.dumps(
                [entry.to_dict() for entry in self._entries],
                ensure_ascii=False,
            )

            # Шифрование данных
            encrypted_data = self._encryption.encrypt_data(entries_json)

            # Формирование структуры файла хранилища
            vault_data = {
                "salt": base64.b64encode(self._encryption.salt).decode("utf-8"),
                "data": encrypted_data,
            }

            # Запись в файл
            with open(self._db_path, "w", encoding="utf-8") as f:
                json.dump(vault_data, f, ensure_ascii=False, indent=2)

        except Exception as e:
            raise IOError(f"Ошибка сохранения базы данных: {e}") from e

    def change_master_password(self, new_password: str) -> None:
        """Смена мастер-пароля хранилища.

        Генерирует новую соль, выводит новый ключ и перешифровывает
        все данные. Текущие записи в памяти не изменяются.

        Аргументы:
            new_password (str): Новый мастер-пароль.

        Исключения:
            ValueError: Если новый пароль пуст.
        """
        salt = self._encryption.generate_salt()
        self._encryption.derive_key(new_password, salt)
        self._save()
