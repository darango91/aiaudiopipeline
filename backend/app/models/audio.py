from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class AudioSession(Base):
    """
    Model for audio sessions.
    """
    __tablename__ = "audio_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)  # UUID as string
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")  # active, completed, etc.
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with transcripts
    transcripts = relationship("Transcript", back_populates="session", cascade="all, delete-orphan")


class Transcript(Base):
    """
    Model for audio transcripts.
    """
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("audio_sessions.id"), nullable=False)
    audio_file_path = Column(String(255), nullable=True)  # Path to stored audio file
    text = Column(Text, nullable=False)  # Full transcript text
    language = Column(String(10), nullable=True)  # Detected language code
    duration = Column(Integer, nullable=True)  # Audio duration in seconds
    meta_data = Column(JSON, nullable=True)  # Additional metadata like confidence scores
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship with audio session
    session = relationship("AudioSession", back_populates="transcripts")
