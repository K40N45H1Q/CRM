from fastapi import APIRouter, Depends

from ..auth import login_user, logout_user, get_current_user
from ..auth import LoginPayload

router = APIRouter(tags=["auth"])


@router.post("/login")
def login(payload: LoginPayload):
    return login_user(payload)


@router.post("/logout")
def logout(user: str = Depends(get_current_user)):
    logout_user()
    return {"status": "ok"}


@router.get("/auth-check")
def auth_check(user: str = Depends(get_current_user)):
    return {"user": user}
