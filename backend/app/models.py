"""Pydantic-модели (схемы) для валидации входящих данных и ответов."""

from typing import Dict, List, Optional

from pydantic import BaseModel, ConfigDict


class UserModel(BaseModel):
    """Схема пользователя для создания/обновления."""
    model_config = ConfigDict(from_attributes=True)
    _id: Optional[str] = None
    fullName: Optional[str] = None
    pin: Optional[str] = None
    documentNumber: Optional[str] = None
    declaredAddress: Optional[str] = None
    residentialAddress: Optional[str] = None
    bank: Optional[str] = None
    swift: Optional[str] = None
    iban: Optional[str] = None
    phoneNumber: Optional[str] = None
    email: Optional[str] = None
    carId: Optional[str] = None
    status: Optional[str] = None
    agreementNumber: Optional[str] = None
    signingDate: Optional[str] = None
    expirationDate: Optional[str] = None
    agreementDuration: Optional[int] = None
    leaseRate: Optional[float] = None
    downPayment: Optional[float] = None
    downPaymentAmount: Optional[float] = None
    monthlyPayment: Optional[float] = None
    preparationFee: Optional[float] = None
    totalAmount: Optional[float] = None
    paidAmount: Optional[float] = None
    debtRemaining: Optional[float] = None
    lastPaymentDate: Optional[str] = None
    paymentDate: Optional[str] = None


class CarModel(BaseModel):
    """Схема автомобиля."""
    model_config = ConfigDict(from_attributes=True)
    _id: Optional[str] = None
    makeModel: Optional[str] = None
    yearOfManufacture: Optional[int] = None
    vin: Optional[str] = None
    plate: Optional[str] = None
    mileage: Optional[int] = None
    cost: Optional[float] = None
    status: Optional[str] = "available"


class SettingsModel(BaseModel):
    """Схема настроек компании."""
    model_config = ConfigDict(from_attributes=True)
    _id: Optional[str] = None
    type: str = "company_lease"
    companyName: Optional[str] = ""
    registrationNo: Optional[str] = ""
    legalAddress: Optional[str] = ""
    representedBy: Optional[str] = ""
    bank: Optional[str] = ""
    swift: Optional[str] = ""
    iban: Optional[str] = ""
    phoneNumber: Optional[str] = ""
    email: Optional[str] = ""
    visibleColumnsUsers: List[str] = []
    visibleColumnsCars: List[str] = []
    columnLabels: Dict[str, str] = {}
    defaultLeaseRate: Optional[float] = 10.0
    defaultDownPaymentPercent: Optional[float] = 0.0
    defaultPreparationFee: Optional[float] = 0.0
