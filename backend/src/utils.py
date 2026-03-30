from secrets import token_urlsafe

from bcrypt import gensalt, hashpw, checkpw
from dotenv import get_key, set_key
from fastapi import Cookie, Response
from jwt import InvalidTokenError, decode, encode
from sqlmodel import select

from src.orm.database import async_session
from src.orm.models import User

ENV_PATH = ".env"
ALGORITHM = "HS256"
COOKIE_KEY="session"
ENV_VAR = "SIGNING_KEY"
SIGNING_KEY = get_key(ENV_PATH, ENV_VAR)

def defend(session: str = Cookie(None)):
    global SIGNING_KEY

    if not SIGNING_KEY:
        set_key(ENV_PATH, ENV_VAR, token_urlsafe(32))
        SIGNING_KEY = get_key(ENV_PATH, ENV_VAR)

    if not session:
        return Response(status_code=404)

    try:
        return decode(session, SIGNING_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        return Response(status_code=404)


async def create_user(username, password, group):
    async with async_session() as session:
        existing_user = (await session.execute(
            select(User).where(User.username == username)
        )).scalar()

        if not existing_user:
            hashed_pw = hashpw(password.encode(), gensalt()).decode()
            new_user = User(
                username=username,
                password=hashed_pw,
                group=group or "default"
            )
            session.add(new_user)
            await session.commit()
            await session.refresh(new_user)


async def verify_password(username, password):
    async with async_session() as session:
        existing_user = (await session.execute(
            select(User).where(User.username == username)
        )).scalar()

        if existing_user and checkpw(
            password=password.encode(),
            hashed_password=existing_user.password.encode()
        ):
            return encode(
                {"sub": existing_user.username},
                SIGNING_KEY, algorithm=ALGORITHM
            )