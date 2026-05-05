"""Конфигурация приложения и константы."""

from pathlib import Path

# Путь для загрузки файлов
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# MongoDB
MONGO_URI = "mongodb://localhost:27017"
DB_NAME = "l_data73"

# Настройки по умолчанию для компании
DEFAULT_SETTINGS = {
    "type": "company_lease",
    "companyName": "ООО «Лизинг Про»",
    "registrationNo": "1234567890",
    "legalAddress": "г. Москва, ул. Примерная, д. 1",
    "representedBy": "Генеральный директор Петров П.П.",
    "bank": "ПАО Сбербанк",
    "swift": "SABRRUMM",
    "iban": "RU0000000000000000000",
    "phoneNumber": "+7 (999) 000-00-00",
    "email": "info@leasing-pro.ru",
    "defaultLeaseRate": 10.0,
    "defaultDownPaymentPercent": 20.0,
    "defaultPreparationFee": 300.0,
    "visibleColumnsUsers": [
        "fullName", "phoneNumber", "email", "status", "carId",
        "agreementNumber", "monthlyPayment", "paymentDate", "debtRemaining"
    ],
    "visibleColumnsCars": ["makeModel", "plate", "vin", "status", "cost"],
    "columnLabels": {}
}
