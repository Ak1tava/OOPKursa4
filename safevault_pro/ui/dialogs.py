# -*- coding: utf-8 -*-
"""Модуль диалоговых окон приложения SafeVault Pro.

Содержит классы диалоговых окон для добавления/редактирования
записей и смены мастер-пароля.
"""

import re

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, List

from models.password_model import PasswordModel
from core.generator import PasswordGenerator
from ui.icons import create_icon

# Константы дизайна
COLORS = {
    "bg_dark": "#0f172a",
    "bg_card": "#1e293b",
    "bg_input": "#1e293b",
    "accent": "#6366f1",
    "accent_hover": "#818cf8",
    "text_primary": "#f1f5f9",
    "text_secondary": "#94a3b8",
    "border": "#334155",
    "success": "#22c55e",
    "warning": "#f59e0b",
    "danger": "#ef4444",
}

CATEGORIES = ["Соцсети", "Учеба", "Банки", "Игры", "Работа", "Другое"]
ALLOWED_EMAIL_DOMAINS = {
    "bk.ru",
    "mail.ru",
    "gmail.com",
    "yahoo.com",
    "yahoo.ru",
}
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class PasswordDialog(ctk.CTkToplevel):
    """Диалоговое окно для добавления или редактирования записи пароля.

    Модальное окно с формой ввода данных, встроенным генератором
    паролей и индикатором надёжности (CTkProgressBar).

    Атрибуты:
        result (PasswordModel | None): Результат — заполненная модель или None.
        generator (PasswordGenerator): Экземпляр генератора паролей.
        entry (PasswordModel | None): Существующая запись (при редактировании).
    """

    def __init__(self, parent, emails: List[str],
                 entry: Optional[PasswordModel] = None):
        """Инициализация диалога.

        Аргументы:
            parent: Родительское окно.
            emails (List[str]): Список существующих email-адресов.
            entry (PasswordModel | None): Запись для редактирования (None — создание).
        """
        super().__init__(parent)
        self.result: Optional[PasswordModel] = None
        self.generator = PasswordGenerator()
        self.entry = entry
        self._password_visible = False
        self._icons = self._build_icon_cache()

        self.title("Редактирование" if entry else "Новая запись")
        self.geometry("480x720")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()

        self._build_form(emails)
        if entry:
            self._populate(entry)
        self.after(100, lambda: self.focus_force())

    def _build_icon_cache(self) -> dict:
        """Создание локального набора иконок для диалогового окна."""
        title_icon = "edit" if self.entry else "plus"
        return {
            "title": create_icon(title_icon, 20, COLORS["text_primary"]),
            "eye": create_icon("eye", 18, COLORS["text_primary"]),
            "dice": create_icon("dice", 18, COLORS["text_primary"]),
            "tools": create_icon("settings", 18, COLORS["text_primary"]),
        }

    def _build_form(self, emails: List[str]):
        """Построение формы ввода."""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=10)

        title = "Редактирование" if self.entry else "Новая запись"
        title_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        title_frame.pack(pady=(5, 15))
        ctk.CTkLabel(title_frame, text="", image=self._icons["title"]).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text=title,
                     font=ctk.CTkFont(size=20, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")

        # --- Название сервиса ---
        ctk.CTkLabel(scroll, text="Название сервиса *",
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x")
        self.service_entry = ctk.CTkEntry(
            scroll, height=38, fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            placeholder_text="Например: Google, GitHub...")
        self.service_entry.pack(fill="x", pady=(2, 10))

        # --- Логин ---
        ctk.CTkLabel(scroll, text="Логин *",
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x")
        self.login_entry = ctk.CTkEntry(
            scroll, height=38, fg_color=COLORS["bg_card"],
            border_color=COLORS["border"],
            placeholder_text="Имя пользователя или email")
        self.login_entry.pack(fill="x", pady=(2, 10))

        # --- Пароль ---
        ctk.CTkLabel(scroll, text="Пароль *",
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x")
        pass_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        pass_frame.pack(fill="x", pady=(2, 4))
        self.password_entry = ctk.CTkEntry(
            pass_frame, height=38, fg_color=COLORS["bg_card"],
            border_color=COLORS["border"], show="•",
            placeholder_text="Введите или сгенерируйте")
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 4))
        self.password_entry.bind("<KeyRelease>", self._update_strength)

        ctk.CTkButton(pass_frame, text="", image=self._icons["eye"], width=38, height=38,
                      fg_color=COLORS["bg_card"], hover_color=COLORS["border"],
                      command=self._toggle_password_visibility).pack(side="left", padx=2)
        ctk.CTkButton(pass_frame, text="", image=self._icons["dice"], width=38, height=38,
                      fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                      command=self._generate_password).pack(side="left", padx=2)

        # --- Индикатор надёжности ---
        strength_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        strength_frame.pack(fill="x", pady=(0, 10))
        self.strength_bar = ctk.CTkProgressBar(
            strength_frame, height=8, progress_color=COLORS["danger"])
        self.strength_bar.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.strength_bar.set(0)
        self.strength_label = ctk.CTkLabel(
            strength_frame, text="—", width=80,
            text_color=COLORS["text_secondary"],
            font=ctk.CTkFont(size=12))
        self.strength_label.pack(side="right")

        # --- Категория ---
        ctk.CTkLabel(scroll, text="Категория",
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x")
        self.category_combo = ctk.CTkComboBox(
            scroll, values=CATEGORIES, height=38,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            button_color=COLORS["accent"],
            dropdown_fg_color=COLORS["bg_card"],
            state="readonly")
        self.category_combo.set("Другое")
        self.category_combo.pack(fill="x", pady=(2, 10))

        # --- Привязанная почта ---
        ctk.CTkLabel(scroll, text="Привязанная почта",
                     text_color=COLORS["text_secondary"],
                     anchor="w").pack(fill="x")
        email_values = emails if emails else []
        self.email_entry = ctk.CTkComboBox(
            scroll, values=email_values, height=38,
            fg_color=COLORS["bg_card"], border_color=COLORS["border"],
            button_color=COLORS["accent"],
            dropdown_fg_color=COLORS["bg_card"])
        self.email_entry.set("")
        self.email_entry.pack(fill="x", pady=(2, 10))

        # --- Генератор паролей ---
        gen_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"],
                                 corner_radius=10, border_width=1,
                                 border_color=COLORS["border"])
        gen_frame.pack(fill="x", pady=(5, 10))

        generator_title = ctk.CTkFrame(gen_frame, fg_color="transparent")
        generator_title.pack(pady=(10, 5))
        ctk.CTkLabel(generator_title, text="", image=self._icons["tools"]).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(generator_title, text="Генератор паролей",
                     font=ctk.CTkFont(size=14, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")

        self.length_label = ctk.CTkLabel(gen_frame, text="Длина: 16",
                                         text_color=COLORS["text_secondary"])
        self.length_label.pack()
        self.length_slider = ctk.CTkSlider(
            gen_frame, from_=6, to=40, number_of_steps=34,
            fg_color=COLORS["border"], progress_color=COLORS["accent"],
            button_color=COLORS["accent_hover"],
            command=self._on_length_change)
        self.length_slider.set(16)
        self.length_slider.pack(fill="x", padx=20, pady=4)

        checks_frame = ctk.CTkFrame(gen_frame, fg_color="transparent")
        checks_frame.pack(pady=(4, 10))
        self.upper_var = ctk.BooleanVar(value=True)
        self.lower_var = ctk.BooleanVar(value=True)
        self.digits_var = ctk.BooleanVar(value=True)
        self.special_var = ctk.BooleanVar(value=True)

        for text, var in [("A-Z", self.upper_var), ("a-z", self.lower_var),
                          ("0-9", self.digits_var), ("!@#", self.special_var)]:
            ctk.CTkCheckBox(checks_frame, text=text, variable=var,
                            command=self._validate_generator_options,
                            fg_color=COLORS["accent"],
                            hover_color=COLORS["accent_hover"],
                            font=ctk.CTkFont(size=12)).pack(side="left", padx=6)

        self.generator_error_label = ctk.CTkLabel(
            gen_frame, text="", text_color=COLORS["danger"],
            font=ctk.CTkFont(size=12))
        self.generator_error_label.pack(pady=(0, 8))

        # --- Кнопки ---
        btn_frame = ctk.CTkFrame(scroll, fg_color="transparent")
        btn_frame.pack(fill="x", pady=(10, 5))
        ctk.CTkButton(btn_frame, text="Сохранить", height=42,
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      font=ctk.CTkFont(size=14, weight="bold"),
                      command=self._save).pack(side="left", fill="x",
                                               expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="Отмена", height=42,
                      fg_color=COLORS["bg_card"],
                      hover_color=COLORS["border"],
                      font=ctk.CTkFont(size=14),
                      command=self.destroy).pack(side="right", fill="x",
                                                  expand=True, padx=(5, 0))

    def _populate(self, entry: PasswordModel):
        """Заполнение полей данными существующей записи."""
        self.service_entry.insert(0, entry.service_name)
        self.login_entry.insert(0, entry.login)
        self.password_entry.insert(0, entry.password)
        self.category_combo.set(entry.category if entry.category in CATEGORIES else "Другое")
        self.email_entry.set(entry.linked_email)
        self._update_strength()

    def _toggle_password_visibility(self):
        """Переключение видимости пароля."""
        self._password_visible = not self._password_visible
        self.password_entry.configure(show="" if self._password_visible else "•")

    def _on_length_change(self, value):
        """Обработка изменения длины пароля на слайдере."""
        self.length_label.configure(text=f"Длина: {int(value)}")

    def _validate_generator_options(self) -> bool:
        """Проверка выбора хотя бы одного набора символов."""
        has_option = any((
            self.upper_var.get(),
            self.lower_var.get(),
            self.digits_var.get(),
            self.special_var.get(),
        ))
        self.generator_error_label.configure(
            text="" if has_option else "выберите хотя бы один из пунктов")
        return has_option

    def _generate_password(self):
        """Генерация пароля с текущими настройками."""
        if not self._validate_generator_options():
            return
        pwd = PasswordGenerator.generate(
            length=int(self.length_slider.get()),
            use_upper=self.upper_var.get(),
            use_lower=self.lower_var.get(),
            use_digits=self.digits_var.get(),
            use_special=self.special_var.get())
        self.password_entry.delete(0, "end")
        self.password_entry.insert(0, pwd)
        if self._password_visible is False:
            self._password_visible = True
            self.password_entry.configure(show="")
        self._update_strength()

    @staticmethod
    def _is_valid_email(email: str) -> bool:
        """Проверка формата и популярного домена почты."""
        if not EMAIL_PATTERN.match(email):
            return False
        domain = email.rsplit("@", 1)[1].lower()
        return domain in ALLOWED_EMAIL_DOMAINS

    def _update_strength(self, event=None):
        """Обновление индикатора надёжности пароля."""
        pwd = self.password_entry.get()
        score, label, color = PasswordGenerator.evaluate_strength(pwd)
        self.strength_bar.set(score / 100)
        self.strength_bar.configure(progress_color=color)
        self.strength_label.configure(text=label, text_color=color)

    def _save(self):
        """Сохранение записи и закрытие диалога."""
        svc = self.service_entry.get().strip()
        login = self.login_entry.get().strip()
        pwd = self.password_entry.get().strip()
        if not svc or not login or not pwd:
            messagebox.showwarning("Ошибка",
                                   "Заполните все обязательные поля (*) !",
                                   parent=self)
            return
        linked_email = self.email_entry.get().strip()
        if linked_email and not self._is_valid_email(linked_email):
            messagebox.showwarning(
                "Ошибка",
                "Введите корректную почту с @ и доменом bk.ru, mail.ru, gmail.com или yahoo.com.",
                parent=self)
            return
        category = self.category_combo.get()
        if category not in CATEGORIES:
            category = "Другое"
        self.result = PasswordModel(
            service_name=svc, login=login, password=pwd,
            category=category,
            linked_email=linked_email,
            is_favorite=self.entry.is_favorite if self.entry else False,
            id=self.entry.id if self.entry else None)
        # Если id=None, dataclass сгенерирует UUID по умолчанию — пересоздадим
        if self.entry is None:
            import uuid
            self.result.id = str(uuid.uuid4())
        self.destroy()


class ChangePasswordDialog(ctk.CTkToplevel):
    """Диалог смены мастер-пароля.

    Атрибуты:
        new_password (str | None): Новый пароль при успешной смене.
    """

    def __init__(self, parent):
        super().__init__(parent)
        self.new_password: Optional[str] = None
        self._icons = {"lock": create_icon("lock_key", 20, COLORS["text_primary"])}
        self.title("Смена мастер-пароля")
        self.geometry("400x320")
        self.resizable(False, False)
        self.configure(fg_color=COLORS["bg_dark"])
        self.transient(parent)
        self.grab_set()
        self._build()
        self.after(100, lambda: self.focus_force())

    def _build(self):
        """Построение формы смены пароля."""
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.pack(pady=(25, 8))
        ctk.CTkLabel(title_frame, text="", image=self._icons["lock"]).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame, text="Смена мастер-пароля",
                     font=ctk.CTkFont(size=18, weight="bold"),
                     text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(
            self,
            text="Новый пароль будет использоваться при следующем входе в приложение.",
            text_color=COLORS["text_secondary"],
            wraplength=320,
            justify="center",
        ).pack(padx=30, pady=(0, 20))

        for lbl_text, attr_name, placeholder in [
            ("Новый пароль:", "new_entry", "Введите новый пароль"),
            ("Подтверждение:", "confirm_entry", "Повторите пароль"),
        ]:
            ctk.CTkLabel(self, text=lbl_text,
                         text_color=COLORS["text_secondary"]).pack(padx=30, anchor="w")
            entry = ctk.CTkEntry(self, height=38, show="•",
                                 fg_color=COLORS["bg_card"],
                                 border_color=COLORS["border"],
                                 placeholder_text=placeholder)
            entry.pack(fill="x", padx=30, pady=(2, 12))
            setattr(self, attr_name, entry)

        ctk.CTkButton(self, text="Сменить пароль", height=42,
                      fg_color=COLORS["accent"],
                      hover_color=COLORS["accent_hover"],
                      command=self._confirm).pack(fill="x", padx=30, pady=(10, 5))
        ctk.CTkButton(self, text="Отмена", height=38,
                      fg_color=COLORS["bg_card"],
                      hover_color=COLORS["border"],
                      command=self.destroy).pack(fill="x", padx=30)

    def _confirm(self):
        """Валидация и подтверждение смены пароля."""
        new_pwd = self.new_entry.get().strip()
        confirm = self.confirm_entry.get().strip()
        if len(new_pwd) < 4:
            messagebox.showwarning("Ошибка",
                                   "Пароль должен быть не менее 4 символов!",
                                   parent=self)
            return
        if new_pwd != confirm:
            messagebox.showwarning("Ошибка", "Пароли не совпадают!", parent=self)
            return
        self.new_password = new_pwd
        self.destroy()
