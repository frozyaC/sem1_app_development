# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Пример для PostgreSQL, замените данные подключения
DATABASE_URL = "sqlite:///mydb.sqlite3"

engine = create_engine(DATABASE_URL, echo=False, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)