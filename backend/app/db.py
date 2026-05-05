"""Инициализация подключения к MongoDB."""

from pymongo import MongoClient
from .config import DB_NAME, MONGO_URI

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
