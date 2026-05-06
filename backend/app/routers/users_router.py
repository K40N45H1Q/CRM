"""Роутер для работы с пользователями (арендаторами)."""

import calendar
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_current_user
from ..db import db
from ..models import UserModel
from ..services.document_service import attach_contract_pdf_to_owners
from ..services.lease_calculator import prepare_user_payload
from ..utils import ensure_settings, serialize, to_object_id

router = APIRouter(prefix="/users", tags=["users"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=List[dict])
def list_users():
    """Возвращает всех пользователей и обновляет их статусы на основе дат."""
    ensure_settings()
    today = datetime.now().strftime("%Y-%m-%d")

    db.users.update_many(
        {"expirationDate": {"$lt": today}, "status": {"$nin": ["Закрыт", "Истек"]}},
        {"$set": {"status": "Истек"}},
    )

    db.users.update_many(
        {"paymentDate": {"$lt": today}, "status": "В ожидании"},
        {"$set": {"status": "Просрочено"}},
    )

    return [serialize(u) for u in db.users.find()]


@router.post("", response_model=dict)
def create_user(payload: UserModel):
    """Создаёт нового пользователя, рассчитывает параметры лизинга и генерирует PDF договора."""
    data = payload.model_dump(exclude_none=True)
    data = prepare_user_payload(data)
    result_id = db.users.insert_one(data).inserted_id
    created = serialize(db.users.find_one({"_id": result_id}))

    try:
        attach_contract_pdf_to_owners(created["_id"], created.get("carId"), created)
    except Exception as e:
        # Не ломать создание пользователя при проблемах с генерацией PDF
        print(f"⚠️ Не удалось сгенерировать PDF: {e}")

    return created


@router.put("/{uid}", response_model=dict)
def update_user(uid: str, payload: UserModel):
    """Обновляет пользователя и применяет логику обработки статусов и оплат."""
    obj_id = to_object_id(uid)
    if not obj_id:
        raise HTTPException(status_code=400, detail="Invalid user id")

    user = db.users.find_one({"_id": obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    data = payload.model_dump(exclude_none=True)
    today = datetime.now().strftime("%Y-%m-%d")

    if data.get("expirationDate") and data.get("expirationDate") < today:
        if data.get("status") not in ["Закрыт", "Истек"]:
            data["status"] = "Истек"

    if data.get("status") == "Оплачено" and user.get("status") != "Оплачено":
        monthly_payment = user.get("monthlyPayment", 0) or 0
        current_debt = user.get("debtRemaining", 0) or 0

        if monthly_payment > 0:
            new_debt = round(max(0, current_debt - monthly_payment), 2)
            current_paid = user.get("paidAmount", 0) or 0
            new_paid = round(current_paid + monthly_payment, 2)

            data["debtRemaining"] = new_debt
            data["paidAmount"] = new_paid
            data["lastPaymentDate"] = today

            if user.get("paymentDate"):
                try:
                    p_date = datetime.fromisoformat(user["paymentDate"])
                    next_month = p_date.month % 12 + 1
                    next_year = p_date.year + (1 if p_date.month == 12 else 0)
                    max_day = calendar.monthrange(next_year, next_month)[1]
                    day = min(p_date.day, max_day)
                    data["paymentDate"] = datetime(next_year, next_month, day).strftime("%Y-%m-%d")
                except Exception:
                    pass

            if new_debt <= 0:
                data["status"] = "Закрыт"
                data["debtRemaining"] = 0.0
                data["paidAmount"] = user.get("totalAmount", 0)

    if user.get("paymentDate") and user.get("paymentDate") < today:
        current_status = data.get("status", user.get("status"))
        if current_status not in ["Оплачено", "Закрыт", "Истек"]:
            data["status"] = "Просрочено"

    db.users.update_one({"_id": obj_id}, {"$set": data})
    updated_user = db.users.find_one({"_id": obj_id})
    return serialize(updated_user)


@router.delete("/{uid}")
def delete_user(uid: str):
    """Удаляет пользователя и освобождает машину, если была привязана."""
    obj_id = to_object_id(uid)
    if not obj_id:
        raise HTTPException(status_code=400, detail="Invalid user id")

    user = db.users.find_one({"_id": obj_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.get("carId"):
        try:
            db.cars.update_one({"_id": to_object_id(user["carId"])}, {"$set": {"status": "available"}})
        except Exception:
            pass

    db.users.delete_one({"_id": obj_id})
    return {"status": "ok"}
