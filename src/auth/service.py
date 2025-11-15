from sqlmodel import select
from .model import User
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

async def authenticate_user(username: str, password: str, session: AsyncSession) -> User:
    statement = select(User).where(User.username == username)
    result = await session.execute(statement)
    user = result.scalars().first()
    if not user or user.password != password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return user

async def register_user(user: User, session: AsyncSession) -> User:
    statement = select(User).where(User.username == user.username)
    result = await session.execute(statement)
    existing_user = result.scalars().first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
