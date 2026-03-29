import json
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Record(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    record_type: str
    data: str  # JSON string
    files: str # JSON string

class FieldConfig(SQLModel, table=True):
    record_type: str = Field(primary_key=True)
    custom_keys: str # JSON string (list of strings)

sqlite_url = "sqlite:///database.db"
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

# --- РАБОТА С КОНФИГОМ ПОЛЕЙ ---
@app.get("/api/config/{record_type}")
def get_config(record_type: str):
    with Session(engine) as session:
        config = session.get(FieldConfig, record_type)
        if not config: return []
        return json.loads(config.custom_keys)

@app.post("/api/config/{record_type}")
def save_config(record_type: str, keys: List[str]):
    with Session(engine) as session:
        config = session.get(FieldConfig, record_type)
        if config:
            config.custom_keys = json.dumps(keys)
        else:
            config = FieldConfig(record_type=record_type, custom_keys=json.dumps(keys))
        session.add(config)
        session.commit()
        return {"status": "ok"}

# --- РАБОТА С ЗАПИСЯМИ ---
@app.get("/api/records")
def get_records():
    with Session(engine) as session:
        recs = session.exec(select(Record).order_by(Record.id.desc())).all()
        return [{
            "id": r.id, 
            "__recordType": r.record_type, 
            **json.loads(r.data), 
            "files": json.loads(r.files)
        } for r in recs]

@app.post("/api/records")
def create_record(item: Dict[str, Any]):
    rtype = item.pop("__recordType")
    files = item.pop("files", [])
    with Session(engine) as session:
        rec = Record(record_type=rtype, data=json.dumps(item), files=json.dumps(files))
        session.add(rec)
        session.commit()
        return {"id": rec.id}

@app.put("/api/records/{id}")
def update_record(id: int, item: Dict[str, Any]):
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
def delete_record(id: int):
    with Session(engine) as session:
        rec = session.get(Record, id)
        if rec:
            session.delete(rec)
            session.commit()
        return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)