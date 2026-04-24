# -*- coding: utf-8 -*-
"""Точка входа приложения SafeVault Pro.

Запускает графический интерфейс менеджера паролей.
"""

import os
import sys

# Добавление корневой директории проекта в sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

from ui.app import SafeVaultApp


def main():
    """Главная функция запуска приложения."""
    app = SafeVaultApp()
    app.mainloop()


if __name__ == "__main__":
    main()
