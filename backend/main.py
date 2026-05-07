import logging

from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware

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

logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.router.redirect_slashes = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router.router)
app.include_router(settings_router.router)
app.include_router(users_router.router)
app.include_router(cars_router.router)
app.include_router(files_router.router)

root_router = APIRouter(dependencies=[Depends(get_current_user)])


@root_router.get("/db-fields")
def root_db_fields():
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

ensure_settings()