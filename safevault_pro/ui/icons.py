# -*- coding: utf-8 -*-
"""Простые векторные иконки для интерфейса SafeVault Pro."""

from __future__ import annotations

import math

import customtkinter as ctk
from PIL import Image, ImageDraw

_BASE_SIZE = 24


def create_icon(name: str, size: int, color: str) -> ctk.CTkImage:
    """Создать CTkImage по имени иконки."""
    render_size = max(48, size * 2)
    image = _draw_icon(name, render_size, color)
    return ctk.CTkImage(light_image=image, dark_image=image, size=(size, size))


def _draw_icon(name: str, size: int, color: str) -> Image.Image:
    builders = {
        "bank": _draw_bank,
        "book": _draw_book,
        "briefcase": _draw_briefcase,
        "chat": _draw_chat,
        "copy": _draw_copy,
        "dice": _draw_dice,
        "edit": _draw_edit,
        "empty": _draw_empty,
        "eye": _draw_eye,
        "folder": _draw_folder,
        "gamepad": _draw_gamepad,
        "info": _draw_info,
        "list": _draw_list,
        "lock_key": _draw_lock_key,
        "plus": _draw_plus,
        "settings": _draw_settings,
        "star": _draw_star,
        "trash": _draw_trash,
    }
    if name not in builders:
        raise ValueError(f"Неизвестная иконка: {name}")
    return builders[name](size, color)


def _new_canvas(size: int) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def _stroke(size: int, factor: float = 2.0) -> int:
    return max(2, round(size * factor / _BASE_SIZE))


def _p(x: float, y: float, scale: float) -> tuple[float, float]:
    return x * scale, y * scale


def _box(x1: float, y1: float, x2: float, y2: float, scale: float) -> tuple[float, float, float, float]:
    return x1 * scale, y1 * scale, x2 * scale, y2 * scale


def _draw_lock_key(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.1)

    draw.arc(_box(6.5, 4.5, 14.5, 12.5, scale), start=180, end=0, fill=color, width=width)
    draw.rounded_rectangle(_box(5.0, 10.0, 16.5, 19.5, scale), radius=2.8 * scale,
                           outline=color, width=width)
    draw.line([_p(10.8, 13.0, scale), _p(10.8, 16.5, scale)], fill=color, width=width)
    draw.ellipse(_box(15.5, 6.0, 21.0, 11.5, scale), outline=color, width=width)
    draw.line([_p(18.2, 11.2, scale), _p(18.2, 17.5, scale)], fill=color, width=width)
    draw.line([_p(18.2, 14.5, scale), _p(20.2, 14.5, scale)], fill=color, width=width)
    draw.line([_p(18.2, 17.5, scale), _p(19.7, 17.5, scale)], fill=color, width=width)
    return image


def _draw_list(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    for y in (7, 12, 17):
        draw.rounded_rectangle(_box(4.0, y - 1.3, 6.5, y + 1.3, scale), radius=1.0 * scale, fill=color)
        draw.line([_p(9.0, y, scale), _p(19.5, y, scale)], fill=color, width=width)
    return image


def _draw_star(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 1.8)
    center_x, center_y = 12 * scale, 12 * scale
    outer = 8 * scale
    inner = 3.6 * scale
    points = []
    for idx in range(10):
        angle = -math.pi / 2 + idx * math.pi / 5
        radius = outer if idx % 2 == 0 else inner
        points.append((center_x + math.cos(angle) * radius, center_y + math.sin(angle) * radius))
    draw.polygon(points, outline=color, width=width)
    return image


def _draw_chat(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.rounded_rectangle(_box(4.0, 5.0, 20.0, 14.5, scale), radius=4 * scale,
                           outline=color, width=width)
    draw.line([_p(8.5, 14.2, scale), _p(8.5, 18.0, scale), _p(12.5, 14.5, scale)],
              fill=color, width=width, joint="curve")
    return image


def _draw_book(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.rounded_rectangle(_box(5.0, 4.5, 19.0, 19.0, scale), radius=2.2 * scale,
                           outline=color, width=width)
    draw.line([_p(12.0, 4.8, scale), _p(12.0, 19.0, scale)], fill=color, width=width)
    draw.line([_p(8.0, 8.5, scale), _p(10.2, 8.0, scale)], fill=color, width=width)
    draw.line([_p(14.0, 8.0, scale), _p(16.0, 8.5, scale)], fill=color, width=width)
    return image


def _draw_bank(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.polygon([_p(4.0, 9.0, scale), _p(12.0, 4.2, scale), _p(20.0, 9.0, scale)],
                 outline=color, width=width)
    draw.line([_p(5.0, 9.5, scale), _p(19.0, 9.5, scale)], fill=color, width=width)
    draw.line([_p(5.0, 18.8, scale), _p(19.0, 18.8, scale)], fill=color, width=width)
    for x in (8.0, 12.0, 16.0):
        draw.line([_p(x, 10.0, scale), _p(x, 17.8, scale)], fill=color, width=width)
    return image


def _draw_gamepad(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.rounded_rectangle(_box(4.0, 8.0, 20.0, 17.5, scale), radius=4.5 * scale,
                           outline=color, width=width)
    draw.line([_p(8.0, 12.7, scale), _p(11.0, 12.7, scale)], fill=color, width=width)
    draw.line([_p(9.5, 11.2, scale), _p(9.5, 14.2, scale)], fill=color, width=width)
    draw.ellipse(_box(14.2, 10.5, 16.5, 12.8, scale), outline=color, width=width)
    draw.ellipse(_box(16.7, 12.2, 19.0, 14.5, scale), outline=color, width=width)
    return image


def _draw_briefcase(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.rounded_rectangle(_box(4.0, 8.0, 20.0, 18.5, scale), radius=2.5 * scale,
                           outline=color, width=width)
    draw.rounded_rectangle(_box(8.0, 5.0, 16.0, 9.0, scale), radius=1.5 * scale,
                           outline=color, width=width)
    draw.line([_p(4.5, 12.2, scale), _p(19.5, 12.2, scale)], fill=color, width=width)
    return image


def _draw_folder(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    points = [
        _p(3.8, 8.5, scale),
        _p(9.0, 8.5, scale),
        _p(11.0, 6.0, scale),
        _p(20.5, 6.0, scale),
        _p(20.5, 18.5, scale),
        _p(3.8, 18.5, scale),
    ]
    draw.polygon(points, outline=color, width=width)
    draw.line([_p(3.8, 10.0, scale), _p(20.5, 10.0, scale)], fill=color, width=width)
    return image


def _draw_settings(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 1.9)
    center = 12 * scale
    for angle in range(0, 360, 45):
        rad = math.radians(angle)
        start = (center + math.cos(rad) * 6.5 * scale, center + math.sin(rad) * 6.5 * scale)
        end = (center + math.cos(rad) * 9.5 * scale, center + math.sin(rad) * 9.5 * scale)
        draw.line([start, end], fill=color, width=width)
    draw.ellipse(_box(7.2, 7.2, 16.8, 16.8, scale), outline=color, width=width)
    draw.ellipse(_box(10.2, 10.2, 13.8, 13.8, scale), fill=color)
    return image


def _draw_plus(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.4)
    draw.line([_p(12.0, 5.5, scale), _p(12.0, 18.5, scale)], fill=color, width=width)
    draw.line([_p(5.5, 12.0, scale), _p(18.5, 12.0, scale)], fill=color, width=width)
    return image


def _draw_empty(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 1.9)
    draw.rounded_rectangle(_box(4.0, 11.0, 20.0, 18.5, scale), radius=2.5 * scale,
                           outline=color, width=width)
    draw.line([_p(4.5, 13.5, scale), _p(9.0, 13.5, scale), _p(11.2, 16.0, scale),
               _p(12.8, 16.0, scale), _p(15.0, 13.5, scale), _p(19.5, 13.5, scale)],
              fill=color, width=width, joint="curve")
    draw.line([_p(12.0, 5.0, scale), _p(12.0, 10.2, scale)], fill=color, width=width)
    draw.line([_p(9.0, 8.2, scale), _p(12.0, 11.0, scale), _p(15.0, 8.2, scale)],
              fill=color, width=width, joint="curve")
    return image


def _draw_copy(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.rounded_rectangle(_box(8.0, 5.0, 18.5, 16.0, scale), radius=2.0 * scale,
                           outline=color, width=width)
    draw.rounded_rectangle(_box(5.0, 8.0, 15.5, 19.0, scale), radius=2.0 * scale,
                           outline=color, width=width)
    return image


def _draw_edit(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.1)
    draw.line([_p(6.0, 17.5, scale), _p(16.5, 7.0, scale)], fill=color, width=width)
    draw.polygon([_p(16.5, 7.0, scale), _p(19.2, 4.2, scale), _p(20.8, 5.8, scale), _p(18.0, 8.5, scale)],
                 outline=color, width=width)
    draw.line([_p(6.0, 17.5, scale), _p(5.0, 20.0, scale), _p(7.5, 19.0, scale)],
              fill=color, width=width, joint="curve")
    return image


def _draw_trash(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.line([_p(7.0, 7.0, scale), _p(17.0, 7.0, scale)], fill=color, width=width)
    draw.line([_p(9.5, 4.8, scale), _p(14.5, 4.8, scale)], fill=color, width=width)
    draw.rounded_rectangle(_box(7.5, 7.5, 16.5, 19.0, scale), radius=2.0 * scale,
                           outline=color, width=width)
    for x in (10.0, 12.0, 14.0):
        draw.line([_p(x, 10.0, scale), _p(x, 16.5, scale)], fill=color, width=width)
    return image


def _draw_eye(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.arc(_box(4.0, 7.0, 20.0, 17.0, scale), start=200, end=340, fill=color, width=width)
    draw.arc(_box(4.0, 7.0, 20.0, 17.0, scale), start=20, end=160, fill=color, width=width)
    draw.ellipse(_box(10.0, 10.0, 14.0, 14.0, scale), outline=color, width=width)
    return image


def _draw_dice(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 1.9)
    draw.rounded_rectangle(_box(5.0, 5.0, 19.0, 19.0, scale), radius=3.0 * scale,
                           outline=color, width=width)
    for x, y in ((8.3, 8.3), (12.0, 12.0), (15.7, 15.7)):
        draw.ellipse(_box(x - 1.1, y - 1.1, x + 1.1, y + 1.1, scale), fill=color)
    return image


def _draw_info(size: int, color: str) -> Image.Image:
    image, draw = _new_canvas(size)
    scale = size / _BASE_SIZE
    width = _stroke(size, 2.0)
    draw.ellipse(_box(5.0, 5.0, 19.0, 19.0, scale), outline=color, width=width)
    draw.ellipse(_box(11.0, 7.0, 13.0, 9.0, scale), fill=color)
    draw.line([_p(12.0, 10.5, scale), _p(12.0, 16.0, scale)], fill=color, width=width)
    return image
