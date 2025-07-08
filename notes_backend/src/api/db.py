from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./notes.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# PUBLIC_INTERFACE
class User(Base):
    """User table."""
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(128), unique=True, index=True, nullable=False)
    hashed_password = Column(String(256), nullable=False)
    notes = relationship("Note", back_populates="owner")

# PUBLIC_INTERFACE
class Note(Base):
    """Note table."""
    __tablename__ = "notes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(256), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner = relationship("User", back_populates="notes")

# PUBLIC_INTERFACE
def get_db():
    """Yield a new database session (used with FastAPI dependencies)."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Utility to create tables (run once at startup)
def create_tables():
    Base.metadata.create_all(bind=engine)
