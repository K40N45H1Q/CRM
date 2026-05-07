import os
import secrets
from typing import Dict, Optional

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

# Получение логина и пароля из переменных окружения
API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "secret")

# Настройка схемы авторизации Bearer
security = HTTPBearer(auto_error=False)

# Хранение активных токенов в памяти (для примера)
auth_tokens: Dict[str, str] = {}


# Модель данных для входа
class LoginPayload(BaseModel):
    username: str
    password: str


# Модель ответа с токеном
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _verify_credentials(username: str, password: str) -> bool:
    """
    Проверка корректности логина и пароля.
    Используется безопасное сравнение secrets.compare_digest.
    """
    return (
        secrets.compare_digest(username, API_USERNAME)
        and secrets.compare_digest(password, API_PASSWORD)
    )


def create_access_token(username: str) -> str:
    """
    Создание нового токена для пользователя и сохранение его в памяти.
    """
    token = secrets.token_urlsafe(32)
    auth_tokens[token] = username
    return token


def revoke_access_token(token: str) -> None:
    """
    Удаление токена из памяти, выход пользователя из системы.
    """
    auth_tokens.pop(token, None)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    """
    Получение текущего пользователя по токену.
    Если токен отсутствует или неверный, возвращает 401.
    """
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Требуется авторизация",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = auth_tokens.get(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный или просроченный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


def login_user(payload: LoginPayload) -> TokenResponse:
    """
    Аутентификация пользователя и выдача токена.
    """
    if not _verify_credentials(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(payload.username)
    return TokenResponse(access_token=access_token)


def logout_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security)
) -> None:
    """
    Выход пользователя: удаление токена из памяти.
    Если токена нет, просто ничего не делает.
    """
    # Проверяем, что credentials переданы и это Bearer токен
    if credentials is not None and credentials.scheme.lower() == "bearer":
        revoke_access_token(credentials.credentials)