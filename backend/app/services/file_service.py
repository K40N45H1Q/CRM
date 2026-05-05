"""Сервис для работы с файлами: сохранение, удаление, формирование путей."""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ..config import UPLOAD_DIR
from ..db import db


def save_upload_file(owner_id: str, owner_type: str, filename: str, content: bytes) -> Dict[str, Any]:
    """Сохраняет файл на диск и создаёт запись в коллекции files."""
    dir_path = UPLOAD_DIR / owner_type / owner_id
    dir_path.mkdir(parents=True, exist_ok=True)
    ext = Path(filename).suffix or ".bin"
    unique = f"{uuid.uuid4().hex}{ext}"
    path = dir_path / unique
    with open(path, "wb") as f:
        f.write(content)
    doc = {
        "ownerId": owner_id,
        "ownerType": owner_type,
        "originalName": filename,
        "serverName": unique,
        "size": len(content),
        "uploadedAt": datetime.utcnow().isoformat(),
        "url": f"/files/{owner_type}/{owner_id}/{unique}",
    }
    db.files.insert_one(doc)
    return doc


def delete_file_record(fid: str) -> bool:
    """Удаляет запись о файле и сам файл с диска. Возвращает True если удалено."""
    from bson import ObjectId

    doc = db.files.find_one({"_id": ObjectId(fid)})
    if not doc:
        return False
    p = UPLOAD_DIR / doc["ownerType"] / doc["ownerId"] / doc.get("serverName", doc["originalName"])
    try:
        if p.exists():
            p.unlink()
    except Exception:
        pass
    db.files.delete_one({"_id": ObjectId(fid)})
    return True
