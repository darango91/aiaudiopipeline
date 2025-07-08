from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class AudioSession(Base):
    """
    Model for audio sessions.
    """
    __tablename__ = "audio_sessions"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String(50), default="active")
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    transcripts = relationship("Transcript", back_populates="session", cascade="all, delete-orphan")


class Transcript(Base):
    """
    Model for audio transcripts.
    """
    __tablename__ = "transcripts"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("audio_sessions.id"), nullable=False)
    audio_file_path = Column(String(255), nullable=True)
    text = Column(Text, nullable=False)
    language = Column(String(10), nullable=True)
    duration = Column(Integer, nullable=True)
    meta_data = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    session = relationship("AudioSession", back_populates="transcripts")
