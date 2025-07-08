from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel


class NotificationType(str, Enum):
    KEYWORD_DETECTED = "keyword_detected"
    TRANSCRIPTION_UPDATE = "transcription_update"
    TRANSCRIPTION_COMPLETE = "transcription_complete"
    PARTIAL_TRANSCRIPTION = "partial_transcription"
    SESSION_STATUS = "session_status"
    ERROR = "error"


class KeywordDetectionPayload(BaseModel):
    keyword: str
    confidence: float
    transcript_segment: str
    start_time: float
    end_time: float
    talking_points: List[Dict[str, Any]]


class TranscriptionUpdatePayload(BaseModel):
    text: str
    start_time: float
    end_time: float
    speaker: Optional[str] = None
    is_prospect: bool = False
    is_final: bool = True


class SessionStatusPayload(BaseModel):
    status: str
    message: Optional[str] = None


class ErrorPayload(BaseModel):
    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None


class Notification(BaseModel):
    type: NotificationType
    session_id: str
    timestamp: datetime = datetime.utcnow()
    payload: Dict[str, Any]
