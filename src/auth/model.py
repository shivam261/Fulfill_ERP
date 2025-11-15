from sqlmodel import SQLModel, Field

class User(SQLModel, table=True):
    username: str = Field(primary_key=True, index=True)
    password: str = Field(nullable=False,min_length=8)
    client_id: str = Field(nullable=False)
    client_secret: str = Field(nullable=False)
    token_url: str = Field(nullable=False)
    tenant_url: str = Field(nullable=False)
    organization: str = Field(nullable=False)
