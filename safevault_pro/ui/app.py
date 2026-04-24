# -*- coding: utf-8 -*-
"""Модуль главного окна приложения SafeVault Pro.

Содержит класс SafeVaultApp — основной класс графического
интерфейса, наследуемый от customtkinter.CTk. Реализует:
- Экран авторизации с мастер-паролем.
- Боковую панель навигации (Sidebar).
- Отображение списка паролей с карточками.
- Живой поиск, фильтрацию по почте и категориям.
"""

import os
import customtkinter as ctk
from tkinter import messagebox
from typing import List, Optional

from models.password_model import PasswordModel
from core.encryption import EncryptionManager
from core.database import DatabaseEngine
from core.generator import PasswordGenerator
from ui.dialogs import PasswordDialog, ChangePasswordDialog
from ui.icons import create_icon

# ==================== Константы дизайна ====================

COLORS = {
    "bg_dark": "#0f172a",
    "bg_sidebar": "#0c1022",
    "bg_card": "#1e293b",
    "bg_card_hover": "#334155",
    "bg_input": "#1e293b",
    "accent": "#6366f1",
    "accent_hover": "#818cf8",
    "accent_light": "#a5b4fc",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "text_muted": "#64748b",
    "border": "#334155",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
    "danger_hover": "#dc2626",
    "favorite": "#fbbf24",
    "sidebar_active": "#1e293b",
}

CATEGORIES = ["Соцсети", "Учеба", "Банки", "Игры", "Работа", "Другое"]
CATEGORY_ICON_NAMES = {
    "Соцсети": "chat", "Учеба": "book", "Банки": "bank",
    "Игры": "gamepad", "Работа": "briefcase", "Другое": "folder",
}

# Путь к файлу базы данных (рядом с main.py)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "vault.dat")


class SafeVaultApp(ctk.CTk):
    """Основной класс графического интерфейса SafeVault Pro.

    Наследуется от customtkinter.CTk и управляет всеми экранами
    приложения: авторизацией, основным интерфейсом и настройками.

    Атрибуты:
        _encryption (EncryptionManager): Менеджер шифрования.
        _db (DatabaseEngine): Движок базы данных.
        _generator (PasswordGenerator): Генератор паролей.
        _current_view (str): Текущий раздел навигации.
        _current_email (str): Текущий фильтр по email.
        _search_query (str): Текущий поисковый запрос.
        _nav_buttons (dict): Словарь кнопок навигации.
    """

    def __init__(self):
        """Инициализация главного окна приложения."""
        super().__init__()

        # Настройка внешнего вида
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Параметры окна
        self.title("SafeVault Pro — Менеджер паролей")
        self.geometry("960x640")
        self.minsize(800, 550)
        self.configure(fg_color=COLORS["bg_dark"])

        # Инициализация компонентов бизнес-логики
        self._encryption = EncryptionManager()
        self._db = DatabaseEngine(self._encryption, DB_PATH)
        self._generator = PasswordGenerator()

        # Состояние интерфейса
        self._current_view: str = "all"
        self._current_email: str = ""
        self._search_query: str = ""
        self._nav_buttons: dict = {}
        self._nav_button_icons: dict = {}
        self._active_nav_btn: Optional[ctk.CTkButton] = None
        self._icons = self._build_icon_cache()

        # Запуск экрана авторизации
        self._show_login_screen()

    def _build_icon_cache(self) -> dict:
        """Создание набора иконок для основных частей интерфейса."""
        icons = {
            "brand_large": create_icon("lock_key", 60, COLORS["accent_light"]),
            "brand_small": create_icon("lock_key", 20, COLORS["accent_light"]),
            "nav_all_default": create_icon("list", 18, COLORS["text_secondary"]),
            "nav_all_active": create_icon("list", 18, COLORS["text_primary"]),
            "nav_favorites_default": create_icon("star", 18, COLORS["favorite"]),
            "nav_favorites_active": create_icon("star", 18, COLORS["favorite"]),
            "nav_settings_default": create_icon("settings", 18, COLORS["text_secondary"]),
            "nav_settings_active": create_icon("settings", 18, COLORS["text_primary"]),
            "section_all": create_icon("list", 24, COLORS["text_primary"]),
            "section_favorites": create_icon("star", 24, COLORS["favorite"]),
            "section_settings": create_icon("settings", 24, COLORS["text_primary"]),
            "add": create_icon("plus", 15, COLORS["text_primary"]),
            "empty": create_icon("empty", 56, COLORS["accent_light"]),
            "copy": create_icon("copy", 15, COLORS["text_primary"]),
            "edit": create_icon("edit", 15, COLORS["text_primary"]),
            "delete": create_icon("trash", 15, COLORS["text_primary"]),
            "master_password": create_icon("lock_key", 20, COLORS["text_primary"]),
            "info": create_icon("info", 20, COLORS["text_primary"]),
        }

        icons["categories"] = {}
        for category, icon_name in CATEGORY_ICON_NAMES.items():
            icons["categories"][category] = {
                "nav": create_icon(icon_name, 18, COLORS["text_secondary"]),
                "nav_active": create_icon(icon_name, 18, COLORS["text_primary"]),
                "header": create_icon(icon_name, 24, COLORS["text_primary"]),
                "card": create_icon(icon_name, 16, COLORS["accent_light"]),
            }

        return icons

    # ==================== ЭКРАН АВТОРИЗАЦИИ ====================

    def _show_login_screen(self):
        """Отображение экрана ввода мастер-пароля.

        Если хранилище не существует — предлагает создать новое.
        Если существует — предлагает ввести пароль для разблокировки.
        """
        self._login_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"])
        self._login_frame.pack(fill="both", expand=True)

        # Центрирующий контейнер
        center = ctk.CTkFrame(self._login_frame, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Логотип
        ctk.CTkLabel(center, text="", image=self._icons["brand_large"]).pack(pady=(0, 8))
        ctk.CTkLabel(center, text="SafeVault Pro",
                     font=ctk.CTkFont(size=32, weight="bold"),
                     text_color=COLORS["accent_light"]).pack()
        ctk.CTkLabel(center, text="Безопасный менеджер паролей",
                     font=ctk.CTkFont(size=14),
                     text_color=COLORS["text_muted"]).pack(pady=(2, 25))

        is_new = not self._db.vault_exists()

        # Карточка ввода
        card = ctk.CTkFrame(center, fg_color=COLORS["bg_card"],
                            corner_radius=16, border_width=1,
                            border_color=COLORS["border"])
        card.pack(padx=20)

        subtitle = "Создайте мастер-пароль" if is_new else "Введите мастер-пароль"
        ctk.CTkLabel(card, text=subtitle,
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(padx=40, pady=(25, 15))

        self._master_entry = ctk.CTkEntry(
            card, width=300, height=42, show="•",
            fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
            placeholder_text="Мастер-пароль")
        self._master_entry.pack(padx=40, pady=(0, 8))
        self._master_entry.bind("<Return>",
                                lambda e: self._handle_login(is_new))

        if is_new:
            self._confirm_entry = ctk.CTkEntry(
                card, width=300, height=42, show="•",
                fg_color=COLORS["bg_dark"], border_color=COLORS["border"],
                placeholder_text="Подтвердите пароль")
            self._confirm_entry.pack(padx=40, pady=(0, 8))
            self._confirm_entry.bind("<Return>",
                                     lambda e: self._handle_login(is_new))

        btn_text = "Создать хранилище" if is_new else "Разблокировать"
        ctk.CTkButton(
            card, text=btn_text, width=300, height=44,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=15, weight="bold"),
            command=lambda: self._handle_login(is_new)
        ).pack(padx=40, pady=(8, 10))
        ctk.CTkLabel(
            card,
            text="После входа мастер-пароль можно изменить в разделе «Настройки».",
            font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"],
            justify="center",
            wraplength=280,
        ).pack(padx=30, pady=(0, 20))

        self._error_label = ctk.CTkLabel(
            center, text="", text_color=COLORS["danger"],
            font=ctk.CTkFont(size=13))
        self._error_label.pack(pady=(10, 0))

        self._master_entry.focus_set()

    def _handle_login(self, is_new: bool):
        """Обработка попытки входа / создания хранилища.

        Аргументы:
            is_new (bool): True — создание нового хранилища.
        """
        password = self._master_entry.get().strip()

        if len(password) < 4:
            self._error_label.configure(
                text="Пароль должен содержать минимум 4 символа")
            return

        if is_new:
            confirm = self._confirm_entry.get().strip()
            if password != confirm:
                self._error_label.configure(text="Пароли не совпадают")
                return
            try:
                self._db.create_vault(password)
                self._login_frame.destroy()
                self._build_main_interface()
            except Exception as e:
                self._error_label.configure(text=f"Ошибка: {e}")
        else:
            if self._db.unlock_vault(password):
                self._login_frame.destroy()
                self._build_main_interface()
            else:
                self._error_label.configure(text="Неверный мастер-пароль")

    # ==================== ГЛАВНЫЙ ИНТЕРФЕЙС ====================

    def _build_main_interface(self):
        """Построение основного интерфейса после авторизации.

        Создаёт боковую панель (Sidebar) и область контента.
        """
        self._build_sidebar()
        self._build_content_area()
        self._navigate_to("all")

    def _build_sidebar(self):
        """Построение боковой панели навигации."""
        sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg_sidebar"],
                               width=220, corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # Логотип в sidebar
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=15, pady=(18, 20))
        ctk.CTkLabel(logo_frame, text="SafeVault",
                     image=self._icons["brand_small"], compound="left",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["accent_light"]).pack(anchor="w")

        sep = ctk.CTkFrame(sidebar, fg_color=COLORS["border"], height=1)
        sep.pack(fill="x", padx=15, pady=(0, 12))

        # Основные разделы
        sections = [
            ("Все пароли", "all", self._icons["nav_all_default"], self._icons["nav_all_active"]),
            ("Избранное", "favorites", self._icons["nav_favorites_default"], self._icons["nav_favorites_active"]),
        ]
        for text, key, default_icon, active_icon in sections:
            btn = self._create_nav_button(sidebar, text, key, default_icon, active_icon)
            btn.pack(fill="x", padx=10, pady=2)

        settings_btn = self._create_nav_button(
            sidebar,
            "Настройки",
            "settings",
            self._icons["nav_settings_default"],
            self._icons["nav_settings_active"],
        )
        settings_btn.pack(fill="x", padx=10, pady=(8, 2))

        # Разделитель категорий
        ctk.CTkLabel(sidebar, text="КАТЕГОРИИ",
                     font=ctk.CTkFont(size=11, weight="bold"),
                     text_color=COLORS["text_muted"]).pack(
            anchor="w", padx=18, pady=(15, 5))

        for cat in CATEGORIES:
            category_icons = self._icons["categories"][cat]
            btn = self._create_nav_button(
                sidebar, cat, cat, category_icons["nav"], category_icons["nav_active"]
            )
            btn.pack(fill="x", padx=10, pady=1)

        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        # Счётчик записей
        self._count_label = ctk.CTkLabel(
            sidebar, text="", font=ctk.CTkFont(size=11),
            text_color=COLORS["text_muted"])
        self._count_label.pack(pady=(0, 12))

    def _create_nav_button(
        self,
        parent,
        text: str,
        key: str,
        default_icon,
        active_icon,
    ) -> ctk.CTkButton:
        """Создание кнопки навигации в боковой панели.

        Аргументы:
            parent: Родительский виджет.
            text (str): Текст кнопки.
            key (str): Ключ раздела для навигации.

        Возвращает:
            ctk.CTkButton: Настроенная кнопка.
        """
        btn = ctk.CTkButton(
            parent, text=text, height=38, anchor="w",
            image=default_icon, compound="left",
            fg_color="transparent",
            hover_color=COLORS["sidebar_active"],
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=13),
            command=lambda: self._navigate_to(key))
        self._nav_buttons[key] = btn
        self._nav_button_icons[key] = {
            "default": default_icon,
            "active": active_icon,
        }
        return btn

    def _build_content_area(self):
        """Построение основной области контента (справа)."""
        self._content = ctk.CTkFrame(self, fg_color=COLORS["bg_dark"],
                                     corner_radius=0)
        self._content.pack(side="right", fill="both", expand=True)

        # --- Верхняя панель: фильтр по email + поиск + кнопка Добавить ---
        top = ctk.CTkFrame(self._content, fg_color="transparent", height=55)
        top.pack(fill="x", padx=20, pady=(15, 5))
        top.pack_propagate(False)

        # Email фильтр
        self._email_combo = ctk.CTkComboBox(
            top, values=["Все почты"], width=200, height=36,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            button_color=COLORS["accent"],
            dropdown_fg_color=COLORS["bg_card"],
            command=self._on_email_filter_changed)
        self._email_combo.set("Все почты")
        self._email_combo.pack(side="left", padx=(0, 10))

        # Поиск
        self._search_entry = ctk.CTkEntry(
            top, height=36, width=260,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            placeholder_text="Поиск по названию или логину...")
        self._search_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self._search_entry.bind("<KeyRelease>", self._on_search_changed)

        # Кнопка добавления
        ctk.CTkButton(
            top, text="Добавить", image=self._icons["add"], compound="left",
            width=130, height=36,
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self._add_entry
        ).pack(side="right")

        # --- Заголовок раздела ---
        header_frame = ctk.CTkFrame(self._content, fg_color="transparent")
        header_frame.pack(fill="x", padx=22, pady=(8, 8))

        self._section_icon = ctk.CTkLabel(
            header_frame, text="", image=self._icons["section_all"]
        )
        self._section_icon.pack(side="left", anchor="n", padx=(0, 12), pady=(4, 0))

        header_text = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_text.pack(side="left", fill="x", expand=True)

        self._section_title = ctk.CTkLabel(
            header_text, text="Все пароли",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLORS["text_primary"], anchor="w")
        self._section_title.pack(anchor="w")

        self._section_subtitle = ctk.CTkLabel(
            header_text, text="",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_muted"], anchor="w")
        self._section_subtitle.pack(anchor="w", pady=(2, 0))

        # --- Скроллируемый список записей ---
        self._scroll_frame = ctk.CTkScrollableFrame(
            self._content, fg_color="transparent",
            scrollbar_button_color=COLORS["border"],
            scrollbar_button_hover_color=COLORS["accent"])
        self._scroll_frame.pack(fill="both", expand=True, padx=15, pady=(0, 10))

    # ==================== НАВИГАЦИЯ ====================

    def _navigate_to(self, section: str):
        """Переключение раздела навигации.

        Аргументы:
            section (str): Ключ раздела (all, favorites, категория, settings).
        """
        self._current_view = section
        self._search_query = ""
        if hasattr(self, "_search_entry"):
            self._search_entry.delete(0, "end")

        # Обновление подсветки активной кнопки
        for key, btn in self._nav_buttons.items():
            icon_pair = self._nav_button_icons[key]
            if key == section:
                btn.configure(fg_color=COLORS["sidebar_active"],
                              text_color=COLORS["text_primary"],
                              image=icon_pair["active"])
            else:
                btn.configure(fg_color="transparent",
                              text_color=COLORS["text_secondary"],
                              image=icon_pair["default"])

        if section == "settings":
            self._show_settings()
        else:
            self._update_section_header()
            self._refresh_display()

    def _update_section_header(self):
        """Обновление заголовка и подзаголовка текущего раздела."""
        titles = {
            "all": ("Все пароли", "Полный список сохранённых аккаунтов", self._icons["section_all"]),
            "favorites": ("Избранное", "Отмеченные звёздочкой записи", self._icons["section_favorites"]),
        }
        for cat in CATEGORIES:
            titles[cat] = (cat, f"Записи категории «{cat}»", self._icons["categories"][cat]["header"])

        title, subtitle, icon = titles.get(
            self._current_view,
            ("Все пароли", "", self._icons["section_all"]),
        )
        self._section_icon.configure(image=icon)
        self._section_title.configure(text=title)
        self._section_subtitle.configure(text=subtitle)

    # ==================== ФИЛЬТРАЦИЯ И ПОИСК ====================

    def _on_email_filter_changed(self, value: str):
        """Обработка изменения фильтра по email (CTkComboBox).

        Аргументы:
            value (str): Выбранное значение email.
        """
        self._current_email = value if value != "Все почты" else ""
        self._refresh_display()

    def _on_search_changed(self, event=None):
        """Обработка живого поиска при отпускании клавиши (<KeyRelease>).

        Фильтрует список записей на лету по названию сервиса и логину.
        """
        self._search_query = self._search_entry.get().strip()
        self._refresh_display()

    def _get_filtered_entries(self) -> List[PasswordModel]:
        """Получение отфильтрованного списка записей.

        Применяет фильтры в порядке: раздел → email → поиск.

        Возвращает:
            List[PasswordModel]: Отфильтрованный список записей.
        """
        # Шаг 1: фильтр по разделу
        if self._current_view == "favorites":
            entries = self._db.get_favorites()
        elif self._current_view in CATEGORIES:
            entries = self._db.filter_by_category(self._current_view)
        else:
            entries = self._db.get_all_entries()

        # Шаг 2: фильтр по email
        if self._current_email:
            entries = [e for e in entries
                       if e.linked_email == self._current_email]

        # Шаг 3: фильтр по поисковому запросу
        if self._search_query:
            q = self._search_query.lower()
            entries = [e for e in entries
                       if q in e.service_name.lower()
                       or q in e.login.lower()]

        return entries

    # ==================== ОТОБРАЖЕНИЕ ДАННЫХ ====================

    def _refresh_display(self):
        """Полное обновление списка записей в области контента.

        Очищает скроллируемый фрейм и перестраивает все карточки.
        Обновляет комбобокс email-фильтра и счётчик записей.
        """
        # Очистка текущих карточек
        for widget in self._scroll_frame.winfo_children():
            widget.destroy()

        # Обновление email-фильтра
        emails = self._db.get_unique_emails()
        self._email_combo.configure(values=["Все почты"] + emails)

        # Обновление счётчика
        total = self._db.get_entry_count()
        if hasattr(self, "_count_label"):
            self._count_label.configure(text=f"Записей: {total}")

        entries = self._get_filtered_entries()

        if not entries:
            self._show_empty_state()
            return

        for entry in entries:
            self._render_entry_card(entry)

    def _show_empty_state(self):
        """Отображение заглушки при отсутствии записей."""
        empty = ctk.CTkFrame(self._scroll_frame, fg_color="transparent")
        empty.pack(expand=True, pady=60)
        ctk.CTkLabel(empty, text="", image=self._icons["empty"]).pack()
        ctk.CTkLabel(empty, text="Нет записей",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_secondary"]).pack(pady=(10, 4))
        ctk.CTkLabel(empty, text='Нажмите "Добавить", чтобы создать первую запись',
                     font=ctk.CTkFont(size=13),
                     text_color=COLORS["text_muted"]).pack()

    def _render_entry_card(self, entry: PasswordModel):
        """Отрисовка карточки записи пароля.

        Создаёт стилизованный CTkFrame с информацией о записи
        и кнопками действий (Избранное, Копировать, Редактировать, Удалить).

        Аргументы:
            entry (PasswordModel): Запись для отображения.
        """
        card = ctk.CTkFrame(self._scroll_frame,
                            fg_color=COLORS["bg_card"],
                            corner_radius=10, height=72,
                            border_width=1,
                            border_color=COLORS["border"])
        card.pack(fill="x", pady=3, padx=4)
        card.grid_columnconfigure(1, weight=1)

        # Кнопка «Избранное»
        star = "★" if entry.is_favorite else "☆"
        star_color = COLORS["favorite"] if entry.is_favorite else COLORS["text_muted"]
        star_btn = ctk.CTkButton(
            card, text=star, width=36, height=36,
            fg_color="transparent", hover_color=COLORS["bg_card_hover"],
            text_color=star_color,
            font=ctk.CTkFont(size=18),
            command=lambda eid=entry.id: self._toggle_favorite(eid))
        star_btn.grid(row=0, column=0, rowspan=2, padx=(10, 2), pady=8)

        # Название сервиса
        category_icons = self._icons["categories"].get(
            entry.category, self._icons["categories"]["Другое"]
        )
        title_frame = ctk.CTkFrame(card, fg_color="transparent")
        title_frame.grid(row=0, column=1, sticky="sw", padx=6, pady=(10, 0))
        ctk.CTkLabel(title_frame, text="", image=category_icons["card"]).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(
            title_frame, text=entry.service_name,
            font=ctk.CTkFont(size=15, weight="bold"),
            text_color=COLORS["text_primary"], anchor="w"
        ).pack(side="left")

        # Детали: логин, категория, почта
        detail_parts = [f"Логин: {entry.login}", f"Категория: {entry.category}"]
        if entry.linked_email:
            detail_parts.append(f"Почта: {entry.linked_email}")
        detail_text = "   •   ".join(detail_parts)

        ctk.CTkLabel(
            card, text=detail_text,
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"], anchor="w"
        ).grid(row=1, column=1, sticky="nw", padx=6, pady=(0, 10))

        # Кнопки действий
        actions = ctk.CTkFrame(card, fg_color="transparent")
        actions.grid(row=0, column=2, rowspan=2, padx=(4, 10), pady=8)

        btn_style = {"width": 34, "height": 34, "corner_radius": 8, "text": ""}

        ctk.CTkButton(
            actions, image=self._icons["copy"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            command=lambda p=entry.password: self._copy_to_clipboard(p),
            **btn_style
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, image=self._icons["edit"],
            fg_color=COLORS["bg_card_hover"], hover_color=COLORS["border"],
            command=lambda e=entry: self._edit_entry(e),
            **btn_style
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            actions, image=self._icons["delete"],
            fg_color=COLORS["danger"], hover_color=COLORS["danger_hover"],
            command=lambda eid=entry.id: self._delete_entry(eid),
            **btn_style
        ).pack(side="left", padx=2)

    # ==================== CRUD ОПЕРАЦИИ ====================

    def _add_entry(self):
        """Открытие диалога добавления новой записи."""
        emails = self._db.get_unique_emails()
        dialog = PasswordDialog(self, emails=emails)
        self.wait_window(dialog)
        if dialog.result:
            self._db.add_entry(dialog.result)
            self._refresh_display()

    def _edit_entry(self, entry: PasswordModel):
        """Открытие диалога редактирования записи.

        Аргументы:
            entry (PasswordModel): Запись для редактирования.
        """
        emails = self._db.get_unique_emails()
        dialog = PasswordDialog(self, emails=emails, entry=entry)
        self.wait_window(dialog)
        if dialog.result:
            self._db.update_entry(entry.id, dialog.result)
            self._refresh_display()

    def _delete_entry(self, entry_id: str):
        """Удаление записи с подтверждением.

        Аргументы:
            entry_id (str): UUID записи для удаления.
        """
        if messagebox.askyesno("Подтверждение",
                               "Удалить эту запись безвозвратно?"):
            self._db.delete_entry(entry_id)
            self._refresh_display()

    def _toggle_favorite(self, entry_id: str):
        """Переключение статуса «Избранное».

        Аргументы:
            entry_id (str): UUID записи.
        """
        self._db.toggle_favorite(entry_id)
        self._refresh_display()

    def _copy_to_clipboard(self, text: str):
        """Копирование текста в буфер обмена.

        Аргументы:
            text (str): Текст для копирования (пароль).
        """
        try:
            import pyperclip
            pyperclip.copy(text)
            messagebox.showinfo("Скопировано",
                                "Пароль скопирован в буфер обмена.")
        except Exception:
            # Фоллбэк через tkinter
            self.clipboard_clear()
            self.clipboard_append(text)
            messagebox.showinfo("Скопировано",
                                "Пароль скопирован в буфер обмена.")

    # ==================== НАСТРОЙКИ ====================

    def _show_settings(self):
        """Отображение страницы настроек в области контента."""
        self._section_icon.configure(image=self._icons["section_settings"])
        self._section_title.configure(text="Настройки")
        self._section_subtitle.configure(text="Управление хранилищем и мастер-паролем")

        for widget in self._scroll_frame.winfo_children():
            widget.destroy()

        settings_frame = ctk.CTkFrame(self._scroll_frame,
                                      fg_color="transparent")
        settings_frame.pack(fill="x", pady=20, padx=10)

        # Карточка смены пароля
        card1 = ctk.CTkFrame(settings_frame, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border"])
        card1.pack(fill="x", pady=5)
        inner1 = ctk.CTkFrame(card1, fg_color="transparent")
        inner1.pack(fill="x", padx=20, pady=18)
        title_frame1 = ctk.CTkFrame(inner1, fg_color="transparent")
        title_frame1.pack(fill="x")
        ctk.CTkLabel(title_frame1, text="", image=self._icons["master_password"]).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame1, text="Сброс мастер-пароля",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(
            inner1,
            text="После входа в приложение здесь можно задать новый пароль для следующего открытия хранилища.",
            font=ctk.CTkFont(size=12),
            text_color=COLORS["text_secondary"],
            justify="left",
            wraplength=520,
        ).pack(anchor="w", pady=(2, 10))
        ctk.CTkButton(inner1, text="Задать новый мастер-пароль", width=220, height=38,
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      command=self._change_master_password).pack(anchor="w")

        # Карточка «О программе»
        card2 = ctk.CTkFrame(settings_frame, fg_color=COLORS["bg_card"],
                             corner_radius=12, border_width=1,
                             border_color=COLORS["border"])
        card2.pack(fill="x", pady=5)
        inner2 = ctk.CTkFrame(card2, fg_color="transparent")
        inner2.pack(fill="x", padx=20, pady=18)
        title_frame2 = ctk.CTkFrame(inner2, fg_color="transparent")
        title_frame2.pack(fill="x")
        ctk.CTkLabel(title_frame2, text="", image=self._icons["info"]).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame2, text="О программе",
                     font=ctk.CTkFont(size=16, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")

        about_text = (
            "SafeVault Pro v1.0\n"
            "Менеджер паролей с шифрованием Fernet (AES-128-CBC)\n"
            "Ключ выводится из мастер-пароля через PBKDF2-HMAC-SHA256\n\n"
            "Стек: Python • customtkinter • Pillow • cryptography"
        )
        ctk.CTkLabel(inner2, text=about_text,
                     font=ctk.CTkFont(size=12),
                     text_color=COLORS["text_secondary"],
                     justify="left").pack(anchor="w", pady=(4, 0))

    def _change_master_password(self):
        """Открытие диалога смены мастер-пароля."""
        dialog = ChangePasswordDialog(self)
        self.wait_window(dialog)
        if dialog.new_password:
            try:
                self._db.change_master_password(dialog.new_password)
                messagebox.showinfo("Успех",
                                    "Мастер-пароль успешно обновлён.")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сменить пароль:\n{e}")
