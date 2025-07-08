from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.db.session import Base


class Keyword(Base):
    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=True)
    threshold = Column(Float, default=0.7)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    talking_points = relationship("TalkingPoint", back_populates="keyword", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Keyword(id={self.id}, text='{self.text}')>"


class TalkingPoint(Base):
    __tablename__ = "talking_points"

    id = Column(Integer, primary_key=True, index=True)
    keyword_id = Column(Integer, ForeignKey("keywords.id"), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    priority = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))
    
    keyword = relationship("Keyword", back_populates="talking_points")
    
    def __repr__(self):
        return f"<TalkingPoint(id={self.id}, keyword_id={self.keyword_id}, title='{self.title}')>"
