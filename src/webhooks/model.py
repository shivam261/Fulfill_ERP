from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import CITEXT
  
class WebhookURL(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    url: str = Field(sa_column=Column(CITEXT, unique=True))
    status: str = "active"  # e.g., active, inactive