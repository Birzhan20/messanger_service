import os
import logging
from typing import Any, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

from dotenv import load_dotenv


Base = declarative_base()
load_dotenv()

POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
if not POSTGRES_PASSWORD:
    logging.error("POSTGRES_PASSWORD not found in .env")
if not POSTGRES_USER:
    logging.error("POSTGRES_USER not found in .env")

DATABASE_URL = f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@0.0.0.0:5432/mytrade"

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_pre_ping=True # Рекомендуется для обработки разрывов соединения
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession | Any, Any]:
    async with AsyncSessionLocal() as session:
        yield session