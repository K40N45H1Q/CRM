"""Утилиты: сериализация, инициализация настроек и вспомогательные функции."""

import calendar
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId

from .config import DEFAULT_SETTINGS
from .db import db


def serialize(doc: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Преобразует MongoDB-документ в JSON-совместимый словарь."""
    if not doc:
        return doc
    d = doc.copy()
    if "_id" in d:
        d["_id"] = str(d["_id"])
    return d


def ensure_settings() -> None:
    """Гарантирует наличие записи настроек в базе данных."""
    existing = db.settings.find_one({"type": DEFAULT_SETTINGS["type"]})
    if not existing:
        db.settings.insert_one(DEFAULT_SETTINGS)
        return
    updates = {}
    for key, value in DEFAULT_SETTINGS.items():
        if key not in existing:
            updates[key] = value
    if updates:
        db.settings.update_one({"_id": existing["_id"]}, {"$set": updates})


def add_months_safe(start: datetime, months: int) -> Optional[datetime]:
    """Добавляет months месяцев к дате start с корректировкой дня месяца."""
    try:
        month = start.month - 1 + months
        year = start.year + month // 12
        month = month % 12 + 1
        day = min(start.day, calendar.monthrange(year, month)[1])
        return datetime(year, month, day)
    except Exception:
        return None


def to_object_id(val: str):
    """Пытается преобразовать строку в ObjectId, иначе возвращает None."""
    try:
        return ObjectId(val)
    except Exception:
        return None
