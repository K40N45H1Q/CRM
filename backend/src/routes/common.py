from json import dumps, loads
from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import select

from src.orm.database import async_session
from src.orm.models import FieldConfig, Record
from src.utils import COOKIE_KEY, defend, verify_password

router = APIRouter()

# --- АВТОРИЗАЦИЯ ---

@router.post("/api/login")
async def login(data: Dict[str, str], response: Response):
    username = data.get("username")
    password = data.get("password")

    session = await verify_password(username, password)

    if session:
        response.set_cookie(key=COOKIE_KEY, value=session)
        response.status_code = 200
        return response

    return Response(status_code=401)


@router.get("/api/get_session")
def verify_session(response=Depends(defend)):
    if isinstance(response, Response) or response is None:
        return Response(status_code=401)
    return Response(status_code=200)


@router.post("/api/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_KEY)
    response.status_code = 200
    return response


# --- КОНФИГУРАЦИЯ ПОЛЕЙ ---

@router.get("/api/get_config/{record_type}")
async def get_config(record_type: str, response=Depends(defend)):
    if isinstance(response, Response): return response

    async with async_session() as session:
        config = await session.get(FieldConfig, record_type)
        return loads(config.extended_keys) if config else []


@router.post("/api/update_config/{record_type}")
async def update_config(record_type: str, keys: List[str], response=Depends(defend)):
    if isinstance(response, Response): return response

    async with async_session() as session:
        config = await session.get(FieldConfig, record_type)
        json_keys = dumps(keys)

        if config:
            config.extended_keys = json_keys
        else:
            session.add(FieldConfig(record_type=record_type, extended_keys=json_keys))
        
        await session.commit()
        return {"status": "ok"}


# --- ЗАПИСИ (RECORDS) ---

@router.get("/api/records")
async def get_records(response=Depends(defend)):
    if isinstance(response, Response): return response

    async with async_session() as session:
        stmt = select(Record).order_by(Record.id.desc())
        result = await session.execute(stmt)
        
        return [
            {
                "id": r.id,
                "__recordType": r.record_type,
                **loads(r.data),
                "files": loads(r.attached)
            }
            for r in result.scalars().all()
        ]


@router.post("/api/records")
async def create_record(item: Dict[str, Any], response=Depends(defend)):
    if isinstance(response, Response): return response

    rtype = item.pop("__recordType")
    files = item.pop("files", [])

    async with async_session() as session:
        new_record = Record(
            record_type=rtype,
            data=dumps(item),
            attached=dumps(files)
        )
        session.add(new_record)
        await session.commit()
        return {"id": new_record.id}


@router.put("/api/records/{record_id}")
async def update_record(record_id: int, item: Dict[str, Any], response=Depends(defend)):
    if isinstance(response, Response): return response

    async with async_session() as session:
        record = await session.get(Record, record_id)
        if not record:
            raise HTTPException(status_code=404)

        record.record_type = item.pop("__recordType")
        record.attached = dumps(item.pop("files", []))
        record.data = dumps(item)

        await session.commit()
        return {"status": "ok"}


@router.delete("/api/records/{record_id}")
async def delete_record(record_id: int, response=Depends(defend)):
    if isinstance(response, Response): return response

    async with async_session() as session:
        record = await session.get(Record, record_id)
        if record:
            await session.delete(record)
            await session.commit()
        return {"status": "ok"}