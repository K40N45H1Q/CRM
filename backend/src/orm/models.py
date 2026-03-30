from typing import Optional
from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True, nullable=False)
    password: str = Field(nullable=False)
    group: str = Field(default="default", nullable=False)

class Record(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    data: str = Field(nullable=False)
    attached: str = Field(nullable=False)
    record_type: str = Field(index=True, nullable=False)

class FieldConfig(SQLModel, table=True):
    record_type: str = Field(primary_key=True)
    extended_keys: str = Field(default="[]", nullable=False)