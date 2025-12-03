# modules/models.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from config import Config
from datetime import datetime

Base = declarative_base()

class Practice(Base):
    __tablename__ = 'practices'
    
    id = Column(Integer, primary_key=True)
    nr = Column(Integer, unique=True) # Original ID from JSON
    naam = Column(String)
    praktijk = Column(String)
    gem = Column(String)
    adres = Column(String)
    email = Column(String)
    tel = Column(String)
    status = Column(String, default='Nieuw')
    notitie = Column(String)
    artsen_namen = Column(String)
    riziv = Column(String)
    
    # Workflow data stored as JSON or separate columns
    workflow = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

def init_db():
    engine = create_engine(Config.DATABASE_URL)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()
