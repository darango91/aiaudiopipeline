from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, JSON
from sqlalchemy.orm import relationship

from app.db.session import Base


class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, nullable=False)
    text = Column(Text, nullable=False)
    start_time = Column(Float, nullable=False)  # Start time in seconds from beginning of session
    end_time = Column(Float, nullable=False)    # End time in seconds from beginning of session
    speaker = Column(String, nullable=True)     # Speaker identifier if available
    is_prospect = Column(Boolean, default=False)  # Whether this segment is from the prospect
    confidence = Column(Float, nullable=True)   # Confidence score from the transcription service
    detected_keywords = Column(JSON, nullable=True)  # JSON array of detected keywords with confidence
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Transcript(id={self.id}, session_id='{self.session_id}', start_time={self.start_time})>"


class AudioSession(Base):
    __tablename__ = "audio_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True, unique=True, nullable=False)
    title = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    duration = Column(Float, nullable=True)  # Total duration in seconds
    status = Column(String, default="active")  # active, completed, error
    metadata = Column(JSON, nullable=True)  # Additional metadata about the session
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<AudioSession(id={self.id}, session_id='{self.session_id}', status='{self.status}')>"
