"""Роутер для настроек компании и плейсхолдеров шаблонов."""

from fastapi import APIRouter, Depends
from typing import Dict, Any

from ..auth import get_current_user
from ..db import db
from ..models import SettingsModel
from ..utils import ensure_settings, serialize

router = APIRouter(prefix="/company-lease-settings", tags=["settings"], dependencies=[Depends(get_current_user)])


@router.get("", response_model=Dict[str, Any])
def get_settings():
    """Возвращает настройки компании. Гарантирует их наличие в БД."""
    ensure_settings()
    doc = db.settings.find_one({"type": "company_lease"})
    return serialize(doc)


@router.put("", response_model=Dict[str, Any])
def update_settings(payload: SettingsModel):
    """Обновляет настройки компании (частичное обновление)."""
    data = payload.model_dump(exclude_none=True)
    existing = db.settings.find_one({"type": "company_lease"})
    if existing:
        db.settings.update_one({"_id": existing["_id"]}, {"$set": data})
    else:
        db.settings.insert_one(data)
    return serialize(db.settings.find_one({"type": "company_lease"}))


@router.get("/template-placeholders", response_model=Dict[str, Any])
def get_template_placeholders():
    """Возвращает список доступных плейсхолдеров для генерации документов."""
    return {
        "groups": [
            {
                "title": "👤 Арендатор",
                "items": [
                    {"field": "fullName", "label": "ФИО"},
                    {"field": "pin", "label": "PIN"},
                    {"field": "documentNumber", "label": "Паспорт"},
                    {"field": "declaredAddress", "label": "Декл. адрес"},
                    {"field": "residentialAddress", "label": "Факт. адрес"},
                    {"field": "bank", "label": "Банк"},
                    {"field": "swift", "label": "SWIFT"},
                    {"field": "iban", "label": "IBAN"},
                    {"field": "phoneNumber", "label": "Телефон"},
                    {"field": "email", "label": "Email"},
                ],
            },
            {
                "title": "🚗 Авто",
                "items": [
                    {"field": "makeModel", "label": "Марка"},
                    {"field": "yearOfManufacture", "label": "Год"},
                    {"field": "vin", "label": "VIN"},
                    {"field": "plate", "label": "Гос. номер"},
                    {"field": "mileage", "label": "Пробег"},
                    {"field": "cost", "label": "Цена"},
                ],
            },
            {
                "title": "🏢 Компания",
                "items": [
                    {"field": "companyName", "label": "Название"},
                    {"field": "registrationNo", "label": "Рег. номер"},
                    {"field": "legalAddress", "label": "Юр. адрес"},
                    {"field": "representedBy", "label": "Представитель"},
                    {"field": "companyBank", "label": "Банк компании"},
                    {"field": "companySwift", "label": "SWIFT компании"},
                    {"field": "companyIban", "label": "IBAN компании"},
                    {"field": "companyPhone", "label": "Телефон компании"},
                    {"field": "companyEmail", "label": "Email компании"},
                ],
            },
            {
                "title": "📄 Договор",
                "items": [
                    {"field": "agreementNumber", "label": "Номер договора"},
                    {"field": "signingDate", "label": "Дата начала"},
                    {"field": "agreementDuration", "label": "Срок"},
                    {"field": "expirationDate", "label": "Дата окончания"},
                    {"field": "paymentDate", "label": "Дата следующего платежа"},
                    {"field": "leaseRate", "label": "Ставка"},
                    {"field": "downPayment", "label": "Взнос %"},
                    {"field": "downPaymentAmount", "label": "Взнос EUR"},
                    {"field": "preparationFee", "label": "Комиссия"},
                    {"field": "monthlyPayment", "label": "Платёж/мес"},
                    {"field": "totalAmount", "label": "Общая сумма"},
                    {"field": "paidAmount", "label": "Оплачено"},
                    {"field": "debtRemaining", "label": "Остаток"},
                ],
            },
        ]
    }


@router.get("/db-fields", response_model=Dict[str, Any])
def get_db_fields():
    """Возвращает списки полей для пользователей и автомобилей."""
    DEFAULT_USER_FIELDS = [
        "fullName", "pin", "documentNumber", "declaredAddress", "residentialAddress",
        "bank", "swift", "iban", "phoneNumber", "email", "carId", "status",
        "agreementNumber", "signingDate", "expirationDate", "agreementDuration",
        "leaseRate", "downPayment", "downPaymentAmount", "monthlyPayment",
        "preparationFee", "totalAmount", "paidAmount", "debtRemaining",
        "lastPaymentDate", "paymentDate"
    ]
    DEFAULT_CAR_FIELDS = [
        "makeModel", "yearOfManufacture", "vin", "plate", "mileage", "cost", "status"
    ]
    u = db.users.find_one()
    c = db.cars.find_one()
    user_fields = [k for k in u.keys() if k != "_id"] if u else DEFAULT_USER_FIELDS
    car_fields = [k for k in c.keys() if k != "_id"] if c else DEFAULT_CAR_FIELDS
    return {"users": user_fields, "cars": car_fields}
