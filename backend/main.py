import json
import jwt
import bcrypt
from contextlib import asynccontextmanager # Добавлено
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException, Response, Cookie, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select

# --- CONFIG ---
SECRET_KEY = "CYBER_PUNK_SECRET_2026"
ALGORITHM = "HS256"
COOKIE_NAME = "json_web_token"

# --- DB SETUP ---
sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# --- MODELS ---
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    password_hash: str

class Record(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    record_type: str
    data: str 
    files: str

class FieldConfig(SQLModel, table=True):
    record_type: str = Field(primary_key=True)
    custom_keys: str

# --- LIFESPAN (Замена startup event) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Код при запуске (аналог startup)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            hashed_pw = bcrypt.hashpw("admin".encode(), bcrypt.gensalt()).decode()
            session.add(User(username="admin", password_hash=hashed_pw))
            session.commit()
    
    yield  # Здесь приложение работает
    
    # Код при выключении (если нужен)
    pass

# Передаем lifespan в FastAPI
app = FastAPI(lifespan=lifespan)

# CORS
app.add_middleware(
    CORSMiddleware, 
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# --- AUTH DEPENDENCY ---
def get_current_user(json_web_token: str = Cookie(None)):
    if not json_web_token: 
        raise HTTPException(status_code=401, detail="UNAUTHORIZED")
    try:
        payload = jwt.decode(json_web_token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except Exception: 
        raise HTTPException(status_code=401, detail="INVALID SESSION")

# --- REST OF THE ROUTES (Остальные роуты остаются без изменений) ---

@app.post("/api/auth/login")
def login(data: Dict[str, str], response: Response):
    with Session(engine) as session:
        user = session.exec(select(User).where(User.username == data.get("username"))).first()
        if user and bcrypt.checkpw(data.get("password").encode(), user.password_hash.encode()):
            token = jwt.encode({"sub": user.username}, SECRET_KEY, algorithm=ALGORITHM)
            response.set_cookie(
                key=COOKIE_NAME, 
                value=token, 
                httponly=True, 
                samesite="lax",
                secure=False 
            )
            return {"status": "ok"}
    raise HTTPException(status_code=401, detail="ACCESS DENIED")

@app.post("/api/auth/logout")
def logout(response: Response):
    response.delete_cookie(COOKIE_NAME)
    return {"status": "ok"}

@app.get("/api/config/{record_type}")
def get_config(record_type: str, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        config = session.get(FieldConfig, record_type)
        if not config: return []
        return json.loads(config.custom_keys)

@app.post("/api/config/{record_type}")
def save_config(record_type: str, keys: List[str], user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        config = session.get(FieldConfig, record_type)
        if config:
            config.custom_keys = json.dumps(keys)
        else:
            config = FieldConfig(record_type=record_type, custom_keys=json.dumps(keys))
        session.add(config)
        session.commit()
        return {"status": "ok"}

@app.get("/api/records")
def get_records(user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        recs = session.exec(select(Record).order_by(Record.id.desc())).all()
        return [{
            "id": r.id, 
            "__recordType": r.record_type, 
            **json.loads(r.data), 
            "files": json.loads(r.files)
        } for r in recs]

@app.post("/api/records")
def create_record(item: Dict[str, Any], user: dict = Depends(get_current_user)):
    rtype = item.pop("__recordType")
    files = item.pop("files", [])
    with Session(engine) as session:
        rec = Record(record_type=rtype, data=json.dumps(item), files=json.dumps(files))
        session.add(rec)
        session.commit()
        return {"id": rec.id}

@app.put("/api/records/{id}")
def update_record(id: int, item: Dict[str, Any], user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        rec = session.get(Record, id)
        if not rec: raise HTTPException(404)
        rec.record_type = item.pop("__recordType")
        rec.files = json.dumps(item.pop("files", []))
        rec.data = json.dumps(item)
        session.add(rec)
        session.commit()
        return {"status": "ok"}

@app.delete("/api/records/{id}")
def delete_record(id: int, user: dict = Depends(get_current_user)):
    with Session(engine) as session:
        rec = session.get(Record, id)
        if rec:
            session.delete(rec)
            session.commit()
        return {"status": "ok"}