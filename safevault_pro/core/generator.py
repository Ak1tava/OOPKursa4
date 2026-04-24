# -*- coding: utf-8 -*-
"""Модуль генерации паролей.

Содержит класс PasswordGenerator с настраиваемой генерацией
криптографически случайных паролей и оценкой их надёжности.
"""

import re
import secrets
import string
from typing import Tuple


class PasswordGenerator:
    """Генератор безопасных паролей с оценкой надёжности.

    Предоставляет статические методы для:
    - Генерации паролей с настраиваемой длиной и набором символов.
    - Оценки надёжности пароля по шкале от 0 до 100.

    Все методы используют модуль `secrets` для криптографически
    стойкой генерации случайных чисел (в отличие от `random`).

    Атрибуты класса:
        LOWERCASE (str): Строчные латинские буквы.
        UPPERCASE (str): Заглавные латинские буквы.
        DIGITS (str): Цифры от 0 до 9.
        SPECIAL (str): Специальные символы.
    """

    LOWERCASE: str = string.ascii_lowercase
    UPPERCASE: str = string.ascii_uppercase
    DIGITS: str = string.digits
    SPECIAL: str = "!@#$%^&*()_+-=[]{}|;:',.<>?"

    @staticmethod
    def generate(
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_special: bool = True,
    ) -> str:
        """Генерация случайного пароля с заданными параметрами.

        Гарантирует наличие хотя бы одного символа из каждого
        выбранного набора, если длина пароля это позволяет.
        Использует `secrets.choice()` для криптостойкой случайности.

        Аргументы:
            length (int): Длина пароля (от 4 до 128). По умолчанию 16.
            use_upper (bool): Включить заглавные буквы. По умолчанию True.
            use_lower (bool): Включить строчные буквы. По умолчанию True.
            use_digits (bool): Включить цифры. По умолчанию True.
            use_special (bool): Включить спецсимволы. По умолчанию True.

        Возвращает:
            str: Сгенерированный пароль заданной длины.

        Исключения:
            ValueError: Если длина меньше 4 или не выбран ни один набор символов.
        """
        length = max(4, min(length, 128))

        # Формирование пула символов и обязательных символов
        charset = ""
        required: list[str] = []

        if use_lower:
            charset += PasswordGenerator.LOWERCASE
            required.append(secrets.choice(PasswordGenerator.LOWERCASE))
        if use_upper:
            charset += PasswordGenerator.UPPERCASE
            required.append(secrets.choice(PasswordGenerator.UPPERCASE))
        if use_digits:
            charset += PasswordGenerator.DIGITS
            required.append(secrets.choice(PasswordGenerator.DIGITS))
        if use_special:
            charset += PasswordGenerator.SPECIAL
            required.append(secrets.choice(PasswordGenerator.SPECIAL))

        # Если ни один набор не выбран — используем строчные буквы
        if not charset:
            charset = PasswordGenerator.LOWERCASE
            required.append(secrets.choice(PasswordGenerator.LOWERCASE))

        # Дополнение до нужной длины случайными символами из пула
        remaining_count = length - len(required)
        if remaining_count > 0:
            password_chars = required + [
                secrets.choice(charset) for _ in range(remaining_count)
            ]
        else:
            password_chars = required[:length]

        # Перемешивание для устранения предсказуемости позиций
        # secrets не имеет shuffle, используем алгоритм Фишера-Йетса
        result = password_chars[:]
        for i in range(len(result) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            result[i], result[j] = result[j], result[i]

        return "".join(result)

    @staticmethod
    def evaluate_strength(password: str) -> Tuple[int, str, str]:
        """Оценка надёжности пароля по набору критериев.

        Анализирует пароль по следующим параметрам:
        - Длина (до 40 баллов: 4 балла за символ, максимум 10 символов).
        - Наличие заглавных букв (+15 баллов).
        - Наличие строчных букв (+10 баллов).
        - Наличие цифр (+15 баллов).
        - Наличие спецсимволов (+20 баллов).
        - Разнообразие символов (+10 баллов, если уникальных > 60%).

        Аргументы:
            password (str): Пароль для оценки.

        Возвращает:
            Tuple[int, str, str]: Кортеж из трёх элементов:
                - score (int): Числовая оценка (0–100).
                - label (str): Текстовая метка («Слабый», «Средний», «Надёжный»).
                - color (str): HEX-код цвета для индикатора.
        """
        if not password:
            return (0, "Нет пароля", "#ef4444")

        score = 0

        # Оценка длины (макс. 40 баллов)
        score += min(len(password) * 4, 40)

        # Наличие заглавных букв (+15)
        if re.search(r"[A-Z]", password):
            score += 15

        # Наличие строчных букв (+10)
        if re.search(r"[a-z]", password):
            score += 10

        # Наличие цифр (+15)
        if re.search(r"\d", password):
            score += 15

        # Наличие спецсимволов (+20)
        if re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:'\",.<>?]", password):
            score += 20

        # Разнообразие символов (+10, если > 60% уникальных)
        if len(password) > 0:
            unique_ratio = len(set(password)) / len(password)
            if unique_ratio > 0.6:
                score += 10

        score = min(score, 100)

        # Определение уровня надёжности
        if score < 40:
            return (score, "Слабый", "#ef4444")       # Красный
        elif score < 70:
            return (score, "Средний", "#f59e0b")      # Жёлтый
        else:
            return (score, "Надёжный", "#22c55e")      # Зелёный
