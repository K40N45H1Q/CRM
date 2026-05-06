import os
import secrets
from typing import Dict, Optional

from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

API_USERNAME = os.getenv("API_USERNAME", "admin")
API_PASSWORD = os.getenv("API_PASSWORD", "secret")

security = HTTPBearer(auto_error=False)
auth_tokens: Dict[str, str] = {}


class LoginPayload(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


def _verify_credentials(username: str, password: str) -> bool:
    return (
        secrets.compare_digest(username, API_USERNAME)
        and secrets.compare_digest(password, API_PASSWORD)
    )


def create_access_token(username: str) -> str:
    token = secrets.token_urlsafe(32)
    auth_tokens[token] = username
    return token


def revoke_access_token(token: str) -> None:
    auth_tokens.pop(token, None)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security),
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    username = auth_tokens.get(credentials.credentials)
    if not username:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return username


def login_user(payload: LoginPayload) -> TokenResponse:
    if not _verify_credentials(payload.username, payload.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(payload.username)
    return TokenResponse(access_token=access_token)


def logout_user(credentials: Optional[HTTPAuthorizationCredentials] = Security(security)) -> None:
    if credentials and credentials.scheme.lower() == "bearer":
        revoke_access_token(credentials.credentials)
