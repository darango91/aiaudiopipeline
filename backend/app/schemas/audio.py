from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Any

from pydantic import BaseModel, Field


class AudioFormat(str, Enum):
    WAV = "wav"
    MP3 = "mp3"
    OGG = "ogg"
    M4A = "m4a"
    FLAC = "flac"


class AudioSessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ERROR = "error"


class AudioChunk(BaseModel):
    session_id: str
    chunk_data: bytes
    sequence_number: int = 0
    timestamp: float  # Time in seconds from the start of the session
    is_final: bool = False


class AudioSessionCreate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class AudioSessionUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[AudioSessionStatus] = None
    metadata: Optional[Dict[str, Any]] = None


class AudioSessionInDBBase(BaseModel):
    id: int
    session_id: str
    title: str
    description: Optional[str] = None
    status: AudioSessionStatus
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    # For backward compatibility
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        return self.meta_data

    class Config:
        from_attributes = True


class AudioSession(AudioSessionInDBBase):
    class Config:
        from_attributes = True


class TranscriptSegment(BaseModel):
    text: str
    start_time: float
    end_time: float
    speaker: Optional[str] = None
    is_prospect: bool = False
    confidence: Optional[float] = None
    detected_keywords: Optional[List[Dict[str, Any]]] = None


class TranscriptCreate(BaseModel):
    session_id: str
    text: str
    start_time: float
    end_time: float
    speaker: Optional[str] = None
    is_prospect: bool = False
    confidence: Optional[float] = None
    detected_keywords: Optional[List[Dict[str, Any]]] = None


class TranscriptInDBBase(BaseModel):
    id: int
    session_id: int
    audio_file_path: Optional[str] = None
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    meta_data: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    # For backward compatibility
    @property
    def metadata(self) -> Optional[Dict[str, Any]]:
        return self.meta_data

    class Config:
        from_attributes = True


class Transcript(TranscriptInDBBase):
    class Config:
        from_attributes = True


class TranscriptionResult(BaseModel):
    session_id: str
    audio_file_path: Optional[str] = None
    text: str
    language: Optional[str] = None
    duration: Optional[float] = None
    metadata: Optional[Dict[str, Any]] = None
    segments: Optional[List[TranscriptSegment]] = None
    is_final: bool = True
