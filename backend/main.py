# main.py
"""Точка входа приложения. Запуск: python main.py из папки backend."""

import logging
import uvicorn

from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

# Абсолютные импорты — папка app должна находиться рядом с main.py
from app.auth import get_current_user
from app.routers import (
    auth_router,
    cars_router,
    files_router,
    settings_router,
    users_router,
)
from app.utils import ensure_settings
from app.db import db

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lease_api")

app = FastAPI(title="Lease Management API")

# Отключаем автоматические редиректы слэшей (убирает 307 Temporary Redirect)
app.router.redirect_slashes = False

# CORS — открыто для всех источников (при необходимости ограничьте)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Регистрируем роутеры
app.include_router(auth_router.router)
app.include_router(settings_router.router)
app.include_router(users_router.router)
app.include_router(cars_router.router)
app.include_router(files_router.router)

# Дублирующие корневые маршруты для совместимости с фронтендом,
# который может запрашивать /db-fields, /upload, /files/... напрямую.
root_router = APIRouter(dependencies=[Depends(get_current_user)])


@root_router.get("/db-fields")
def root_db_fields():
    """Дублирующий маршрут: GET /db-fields — совместимость с фронтом."""
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


app.include_router(root_router)

# Инициализация настроек при старте
ensure_settings()
logger.info("Lease Management API initialized (started from main.py)")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)