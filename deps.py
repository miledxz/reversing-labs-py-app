import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base


DB_URL = os.getenv("DB_URL", "sqlite:///./weather.db")
engine = create_engine(DB_URL, connect_args={"check_same_thread": False} if DB_URL.startswith("sqlite") else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()