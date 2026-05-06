"""Роутер для загрузки, отдачи и удаления файлов.

Реализованы маршруты:
- POST /api/upload  (оригинал)
- POST /upload      (совместимость с фронтом)
- GET  /api/files/{ot}/{oid}/{fn}
- GET  /files/{ot}/{oid}/{fn}  (совместимость)
- GET  /api/files/{ot}/{oid}
- GET  /files/{ot}/{oid}        (совместимость)
- DELETE /api/files/{fid}
- DELETE /files/{fid}           (совместимость)
"""

import os
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse

from ..auth import get_current_user
from ..db import db
from ..services.file_service import delete_file_record, save_upload_file
from ..utils import serialize

router = APIRouter(tags=["files"], dependencies=[Depends(get_current_user)])

# API-префикс (оригинальные маршруты)
api_prefix = "/api"
router_prefix = ""


@router.post(f"{api_prefix}/upload")
async def upload_file_api(ownerId: str = Form(...), ownerType: str = Form(...), file: UploadFile = File(...)):
    """Загрузка файла (API)."""
    content = await file.read()
    doc = save_upload_file(ownerId, ownerType, file.filename, content)
    return serialize(doc)


@router.post("/upload")
async def upload_file(ownerId: str = Form(...), ownerType: str = Form(...), file: UploadFile = File(...)):
    """Загрузка файла (совместимость с фронтом)."""
    content = await file.read()
    doc = save_upload_file(ownerId, ownerType, file.filename, content)
    return serialize(doc)


@router.get(f"{api_prefix}/files/{{ot}}/{{oid}}/{{fn}}")
def serve_file_api(ot: str, oid: str, fn: str):
    """Отдаёт файл (API)."""
    path = os.path.join("uploads", ot, oid, fn)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=path, filename=fn, headers={"Content-Disposition": f"inline; filename*=UTF-8''{fn}"})


@router.get("/files/{ot}/{oid}/{fn}")
def serve_file(ot: str, oid: str, fn: str):
    """Отдаёт файл (совместимость)."""
    path = os.path.join("uploads", ot, oid, fn)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path=path, filename=fn, headers={"Content-Disposition": f"inline; filename*=UTF-8''{fn}"})


@router.get(f"{api_prefix}/files/{{ot}}/{{oid}}")
def list_files_api(ot: str, oid: str):
    """Список файлов для владельца (API)."""
    return [serialize(f) for f in db.files.find({"ownerType": ot, "ownerId": oid})]


@router.get("/files/{ot}/{oid}")
def list_files(ot: str, oid: str):
    """Список файлов для владельца (совместимость)."""
    return [serialize(f) for f in db.files.find({"ownerType": ot, "ownerId": oid})]


@router.delete(f"{api_prefix}/files/{{fid}}")
def delete_file_api(fid: str):
    """Удаляет файл (API)."""
    ok = delete_file_record(fid)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "ok"}


@router.delete("/files/{fid}")
def delete_file(fid: str):
    """Удаляет файл (совместимость)."""
    ok = delete_file_record(fid)
    if not ok:
        raise HTTPException(status_code=404, detail="File not found")
    return {"status": "ok"}
