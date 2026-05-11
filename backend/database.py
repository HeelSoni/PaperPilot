from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import os

DATABASE_URL = "sqlite:///./database/paperpilot.db"

# Ensure database directory exists
os.makedirs("./database", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class SavedPaper(Base):
    __tablename__ = "saved_papers"

    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(String, unique=True, index=True) # arXiv ID
    title = Column(String)
    authors = Column(Text) # JSON string or comma separated
    abstract = Column(Text)
    link = Column(String)
    saved_at = Column(DateTime, default=datetime.datetime.utcnow)
    notes = Column(Text, nullable=True)

class SearchHistory(Base):
    __tablename__ = "search_history"

    id = Column(Integer, primary_key=True, index=True)
    query = Column(String, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
