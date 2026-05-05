"""Сервис с бизнес-логикой расчётов лизинга и дат."""

import calendar
import json
import random
from datetime import datetime
from typing import Any, Dict, Optional

from bson import ObjectId

from ..config import DEFAULT_SETTINGS
from ..db import db
from ..utils import add_months_safe


def prepare_user_payload(data: Dict[str, Any]) -> Dict[str, Any]:
    """Подготавливает и рассчитывает все поля договора для сохранения в БД."""
    settings = db.settings.find_one({"type": DEFAULT_SETTINGS["type"]}) or {}

    if not data.get("agreementNumber"):
        data["agreementNumber"] = f"LS-{datetime.now().year}-{random.randint(1000, 9999)}"

    if not data.get("signingDate"):
        data["signingDate"] = datetime.now().strftime("%Y-%m-%d")

    if not data.get("agreementDuration"):
        data["agreementDuration"] = 36

    duration = data.get("agreementDuration") or 36

    rate = data.get("leaseRate") if data.get("leaseRate") is not None else settings.get("defaultLeaseRate", 10.0)
    down_pct = data.get("downPayment") if data.get("downPayment") is not None else settings.get("defaultDownPaymentPercent", 0.0)
    prep = data.get("preparationFee") if data.get("preparationFee") is not None else settings.get("defaultPreparationFee", 0.0)
    data["leaseRate"], data["downPayment"], data["preparationFee"] = rate, down_pct, prep

    car_cost = 0.0
    car_data: Dict[str, Any] = {}
    if data.get("carId"):
        try:
            car_doc = db.cars.find_one({"_id": ObjectId(data["carId"])})
            if car_doc:
                car_data = car_doc
                car_cost = float(car_doc.get("cost", 0))
                db.cars.update_one({"_id": ObjectId(data["carId"])}, {"$set": {"status": "busy"}})
        except Exception:
            car_data = {}

    # Заполняем данные автомобиля в договоре для шаблона и сохранения
    if car_data:
        for field in ["makeModel", "yearOfManufacture", "vin", "plate", "mileage"]:
            if field in car_data and field not in data:
                data[field] = car_data[field]

    try:
        start = datetime.fromisoformat(data["signingDate"])
        next_dt = add_months_safe(start, 1)
        data["paymentDate"] = next_dt.strftime("%Y-%m-%d") if next_dt else None
    except Exception:
        data["paymentDate"] = None

    if car_cost > 0 and duration > 0:
        down_amt = round(car_cost * (down_pct / 100), 2)
        financed = car_cost - down_amt
        interest = financed * (rate / 100) * (duration / 12)
        total = round(financed + interest + prep, 2)
        monthly = round(total / duration, 2)
        paid_initial = down_amt + prep
        debt = round(total - paid_initial, 2)

        data.update(
            {
                "downPaymentAmount": down_amt,
                "totalAmount": total,
                "monthlyPayment": monthly,
                "debtRemaining": debt,
                "paidAmount": paid_initial,
                "status": "Оплачено" if debt <= 0 else "В ожидании",
                "cost": car_cost,
            }
        )

        try:
            exp_dt = add_months_safe(start, duration)
            data["expirationDate"] = exp_dt.strftime("%Y-%m-%d") if exp_dt else None
        except Exception:
            data["expirationDate"] = None
    else:
        data["status"] = "В ожидании"
        data["expirationDate"] = None

    tpl = {
        "fullName": data.get("fullName"),
        "pin": data.get("pin"),
        "documentNumber": data.get("documentNumber"),
        "declaredAddress": data.get("declaredAddress"),
        "residentialAddress": data.get("residentialAddress"),
        "userBank": data.get("bank"),
        "userSwift": data.get("swift"),
        "userIban": data.get("iban"),
        "phoneNumber": data.get("phoneNumber"),
        "email": data.get("email"),
        "makeModel": car_data.get("makeModel"),
        "yearOfManufacture": car_data.get("yearOfManufacture"),
        "vin": car_data.get("vin"),
        "plate": car_data.get("plate"),
        "mileage": car_data.get("mileage"),
        "cost": data.get("cost"),
        "companyName": settings.get("companyName"),
        "registrationNo": settings.get("registrationNo"),
        "legalAddress": settings.get("legalAddress"),
        "representedBy": settings.get("representedBy"),
        "companyBank": settings.get("bank"),
        "companySwift": settings.get("swift"),
        "companyIban": settings.get("iban"),
        "companyPhone": settings.get("phoneNumber"),
        "companyEmail": settings.get("email"),
        "agreementNumber": data.get("agreementNumber"),
        "signingDate": data.get("signingDate"),
        "agreementDuration": data.get("agreementDuration"),
        "expirationDate": data.get("expirationDate"),
        "paymentDate": data.get("paymentDate"),
        "leaseRate": data.get("leaseRate"),
        "downPayment": data.get("downPayment"),
        "downPaymentAmount": data.get("downPaymentAmount"),
        "preparationFee": data.get("preparationFee"),
        "monthlyPayment": data.get("monthlyPayment"),
        "totalAmount": data.get("totalAmount"),
        "paidAmount": data.get("paidAmount"),
        "debtRemaining": data.get("debtRemaining"),
        "status": data.get("status"),
    }
    try:
        print("\n" + "=" * 60 + "\n📄 TEMPLATE VARIABLES:\n" + json.dumps(tpl, indent=2, ensure_ascii=False) + "\n" + "=" * 60 + "\n")
    except Exception:
        pass

    data.update(tpl)
    return data
