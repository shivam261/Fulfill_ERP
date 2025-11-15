from sqlmodel import SQLModel, Field
from typing import Optional

class ReceiveNumber(SQLModel):
    a:int
    b:int
    c:int

class ResponseId(SQLModel):
    task_id:str

