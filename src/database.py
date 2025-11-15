import logging
import os
import ssl
from sqlmodel import Session, SQLModel, create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

load_dotenv()

ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

POSTGRES_SERVICE_URL = os.getenv("POSTGRES_SERVICE_URL")
engine = create_async_engine(POSTGRES_SERVICE_URL,connect_args={"ssl": ssl_context}, echo=True)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session():
    async with async_session() as session:
        yield session
