from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    fragments = relationship("Fragment", back_populates="session")

class Fragment(Base):
    __tablename__ = "fragments"
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("sessions.id"))
    content = Column(Text)
    sensory_tags = Column(String)  # JSON string or comma-separated
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    
    # AI Tagged data
    tagged_time = Column(String, nullable=True)
    tagged_location = Column(String, nullable=True)
    tagged_person = Column(String, nullable=True)
    follow_up_question = Column(Text, nullable=True)

    session = relationship("Session", back_populates="fragments")
