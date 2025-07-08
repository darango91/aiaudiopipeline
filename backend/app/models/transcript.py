from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON

from app.db.session import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    speaker = Column(String, nullable=True)
    is_prospect = Column(Boolean, default=False)
    confidence = Column(Float, nullable=True)
    detected_keywords = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, session_id='{self.session_id}', start_time={self.start_time})>"


class AudioSession(Base):
    __tablename__ = "audio_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, unique=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)
    status = Column(String, default="active")
    metadata = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    def __repr__(self):
        return f"<AudioSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"
