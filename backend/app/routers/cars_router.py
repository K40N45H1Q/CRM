"""Роутер для работы с автомобилями."""

from typing import List

from fastapi import APIRouter, HTTPException

from ..db import db
from ..models import CarModel
from ..utils import serialize, to_object_id

router = APIRouter(prefix="/cars", tags=["cars"])


@router.get("", response_model=List[dict])
def list_cars():
    """Возвращает все автомобили."""
    return [serialize(c) for c in db.cars.find()]


@router.get("/available", response_model=List[dict])
def list_available_cars():
    """Возвращает только доступные автомобили."""
    return [serialize(c) for c in db.cars.find({"status": "available"})]


@router.post("", response_model=dict)
def create_car(payload: CarModel):
    """Создаёт автомобиль."""
    data = payload.model_dump(exclude_none=True)
    r = db.cars.insert_one(data)
    return serialize(db.cars.find_one({"_id": r.inserted_id}))


@router.put("/{cid}", response_model=dict)
def update_car(cid: str, payload: CarModel):
    """Обновляет автомобиль."""
    obj_id = to_object_id(cid)
    if not obj_id:
        raise HTTPException(status_code=400, detail="Invalid car id")
    db.cars.update_one({"_id": obj_id}, {"$set": payload.model_dump(exclude_none=True)})
    return serialize(db.cars.find_one({"_id": obj_id}))


@router.delete("/{cid}")
def delete_car(cid: str):
    """Удаляет автомобиль."""
    obj_id = to_object_id(cid)
    if not obj_id:
        raise HTTPException(status_code=400, detail="Invalid car id")
    deleted = db.cars.delete_one({"_id": obj_id}).deleted_count
    if not deleted:
        raise HTTPException(status_code=404, detail="Car not found")
    return {"status": "ok"}
