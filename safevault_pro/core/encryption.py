# -*- coding: utf-8 -*-
"""Модуль шифрования данных.

Содержит класс EncryptionManager, отвечающий за все криптографические
операции приложения: генерацию ключей, хеширование мастер-пароля,
шифрование и дешифрование базы данных с использованием алгоритма Fernet.
"""

import os
import base64
from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


class EncryptionManager:
    """Менеджер шифрования на основе Fernet (симметричное шифрование).

    Обеспечивает безопасное хранение паролей путём:
    - Генерации криптографически стойкой соли (16 байт).
    - Вывода ключа из мастер-пароля с помощью PBKDF2-HMAC-SHA256
      (480 000 итераций, соответствует рекомендациям OWASP 2023).
    - Шифрования/дешифрования данных алгоритмом Fernet (AES-128-CBC + HMAC).

    Атрибуты:
        _fernet (Fernet | None): Экземпляр Fernet для текущего сеанса.
        _salt (bytes | None): Соль, использованная для вывода ключа.
    """

    # Количество итераций PBKDF2 (рекомендация OWASP для SHA-256)
    _ITERATIONS = 480_000

    def __init__(self):
        """Инициализация менеджера шифрования.

        Создаёт экземпляр без активного ключа. Для начала работы
        необходимо вызвать derive_key() с мастер-паролем.
        """
        self._fernet: Fernet | None = None
        self._salt: bytes | None = None

    def generate_salt(self) -> bytes:
        """Генерация криптографически случайной соли.

        Создаёт 16 байт случайных данных через os.urandom(),
        которые используются при выводе ключа из мастер-пароля.

        Возвращает:
            bytes: Сгенерированная соль (16 байт).
        """
        self._salt = os.urandom(16)
        return self._salt

    def derive_key(self, master_password: str, salt: bytes) -> bytes:
        """Вывод ключа шифрования из мастер-пароля методом PBKDF2.

        Использует PBKDF2-HMAC-SHA256 для преобразования текстового
        пароля в 32-байтный ключ, пригодный для Fernet. Результат
        кодируется в URL-safe Base64.

        Аргументы:
            master_password (str): Мастер-пароль пользователя.
            salt (bytes): Соль для вывода ключа (16 байт).

        Возвращает:
            bytes: Производный ключ в формате Base64 (44 байта).

        Исключения:
            ValueError: Если мастер-пароль пуст.
        """
        if not master_password:
            raise ValueError("Мастер-пароль не может быть пустым.")

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=self._ITERATIONS,
        )
        key = base64.urlsafe_b64encode(kdf.derive(master_password.encode("utf-8")))
        self._fernet = Fernet(key)
        self._salt = salt
        return key

    def encrypt_data(self, plaintext: str) -> str:
        """Шифрование строки данных алгоритмом Fernet.

        Преобразует открытый текст в зашифрованный токен Fernet.
        Перед вызовом необходимо инициализировать ключ через derive_key().

        Аргументы:
            plaintext (str): Строка для шифрования (обычно JSON).

        Возвращает:
            str: Зашифрованный токен Fernet в формате Base64.

        Исключения:
            RuntimeError: Если ключ шифрования не был инициализирован.
        """
        if self._fernet is None:
            raise RuntimeError("Ключ шифрования не инициализирован. Вызовите derive_key().")
        encrypted_bytes = self._fernet.encrypt(plaintext.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    def decrypt_data(self, ciphertext: str) -> str:
        """Дешифрование данных из токена Fernet.

        Восстанавливает исходный текст из зашифрованного токена.
        При неверном ключе выбрасывает InvalidToken.

        Аргументы:
            ciphertext (str): Зашифрованный токен Fernet (Base64).

        Возвращает:
            str: Расшифрованная строка (обычно JSON).

        Исключения:
            RuntimeError: Если ключ шифрования не был инициализирован.
            cryptography.fernet.InvalidToken: Если ключ неверен или данные повреждены.
        """
        if self._fernet is None:
            raise RuntimeError("Ключ шифрования не инициализирован. Вызовите derive_key().")
        decrypted_bytes = self._fernet.decrypt(ciphertext.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    @property
    def salt(self) -> bytes | None:
        """Текущая соль, используемая для вывода ключа.

        Возвращает:
            bytes | None: Соль или None, если соль не была задана.
        """
        return self._salt

    @property
    def is_initialized(self) -> bool:
        """Проверка инициализации ключа шифрования.

        Возвращает:
            bool: True, если ключ был успешно выведен.
        """
        return self._fernet is not None
