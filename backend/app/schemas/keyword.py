from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class TalkingPointBase(BaseModel):
    title: str
    content: str
    priority: int = Field(default=1, ge=1, le=10)


class TalkingPointCreate(TalkingPointBase):
    pass


class TalkingPointUpdate(TalkingPointBase):
    title: Optional[str] = None
    content: Optional[str] = None
    priority: Optional[int] = None


class TalkingPointInDBBase(TalkingPointBase):
    id: int
    keyword_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TalkingPoint(TalkingPointInDBBase):
    pass


class KeywordBase(BaseModel):
    text: str
    description: Optional[str] = None
    threshold: float = Field(default=0.7, ge=0.0, le=1.0)


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(KeywordBase):
    text: Optional[str] = None
    description: Optional[str] = None
    threshold: Optional[float] = None


class KeywordInDBBase(KeywordBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Keyword(KeywordInDBBase):
    pass


class KeywordWithTalkingPoints(KeywordInDBBase):
    talking_points: List[TalkingPoint] = []
