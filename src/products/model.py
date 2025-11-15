from sqlmodel import SQLModel, Field
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import CITEXT
class Product(SQLModel, table=True):

    id: int | None = Field(default=None, primary_key=True)
    name: str
    sku: str = Field(sa_column=Column(CITEXT, unique=False))
    description: str | None = None
    status: str = "active"  # e.g., active, inactive



