from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import SQLModel
from uvicorn import run

from src.orm.database import async_engine
from src.routes import common
from src.utils import create_user

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with async_engine.begin() as connection:
        await connection.run_sync(SQLModel.metadata.create_all)
        await create_user("admin", "admin", "admin")
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(common.router)

app.add_middleware(
    CORSMiddleware,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
    allow_origins=["http://localhost:5173"],
)

if __name__ == "__main__":
    run("run:app", host="0.0.0.0", port=8000, reload=True)