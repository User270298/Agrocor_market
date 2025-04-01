# from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
# from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
# from dotenv import load_dotenv
# import os
# 
# load_dotenv()
# Base = declarative_base()
# POSTGRES_USER = os.getenv('POSTGRES_USER')
# POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
# POSTGRES_DB = os.getenv('POSTGRES_DB')
# POSTGRES_HOST = os.getenv('POSTGRES_HOST')
# POSTGRES_PORT = os.getenv('POSTGRES_PORT')
# 
# DATABASE_URL = (f'postgresql+asyncpg://'
#                 f'{POSTGRES_USER}:'
#                 f'{POSTGRES_PASSWORD}@'
#                 f'{POSTGRES_HOST}:'
#                 f'{POSTGRES_PORT}/'
#                 f'{POSTGRES_DB}')
# 
# engine = create_async_engine(DATABASE_URL, echo=False)
# async_session = sessionmaker(
#     engine,
#     class_=AsyncSession,
#     expire_on_commit=False,
# )

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
import os

# Для миграций используем синхронный движок
SYNC_DATABASE_URL = "sqlite:///./agrocor.db"
sync_engine = create_engine(SYNC_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=sync_engine)

Base = declarative_base()

# Используем SQLite вместо PostgreSQL
DATABASE_URL = "sqlite+aiosqlite:///./agrocor.db"  # Файл базы данных SQLite

# Создаем асинхронный движок
engine = create_async_engine(DATABASE_URL, echo=False, future=True)

# Создаем сессию
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)