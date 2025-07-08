from typing import List, Optional
from sqlalchemy.orm import Session
import uuid
from datetime import datetime

from app.models.audio import AudioSession, Transcript
from app.schemas.audio import AudioSessionCreate, AudioSessionUpdate, TranscriptionResult


def create_audio_session(db: Session, session: AudioSessionCreate) -> AudioSession:
    """
    Create a new audio session in the database.
    """
    session_id = str(uuid.uuid4())
    db_session = AudioSession(
        session_id=session_id,
        title=session.title,
        description=session.description,
        status="active",
        meta_data=session.metadata
    )
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


def get_audio_session(db: Session, session_id: str) -> Optional[AudioSession]:
    """
    Get an audio session by its UUID.
    """
    return db.query(AudioSession).filter(AudioSession.session_id == session_id).first()


def get_audio_session_by_id(db: Session, id: int) -> Optional[AudioSession]:
    """
    Get an audio session by its database ID.
    """
    return db.query(AudioSession).filter(AudioSession.id == id).first()


def get_audio_sessions(db: Session, skip: int = 0, limit: int = 100) -> List[AudioSession]:
    """
    Get a list of audio sessions.
    """
    return db.query(AudioSession).offset(skip).limit(limit).all()


def update_audio_session(db: Session, session_id: str, session_update: AudioSessionUpdate) -> Optional[AudioSession]:
    """
    Update an audio session.
    """
    db_session = get_audio_session(db, session_id)
    if db_session:
        update_data = session_update.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_session, key, value)
        db_session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
    return db_session


def delete_audio_session(db: Session, session_id: str) -> bool:
    """
    Delete an audio session.
    """
    db_session = get_audio_session(db, session_id)
    if db_session:
        db.delete(db_session)
        db.commit()
        return True
    return False


def create_transcript(db: Session, session_id: str, transcription: TranscriptionResult) -> Optional[Transcript]:
    """
    Create a new transcript for an audio session.
    """
    db_session = get_audio_session(db, session_id)
    if not db_session:
        return None
    
    db_transcript = Transcript(
        session_id=db_session.id,
        audio_file_path=transcription.audio_file_path,
        text=transcription.text,
        language=transcription.language,
        duration=transcription.duration,
        meta_data=transcription.metadata
    )
    db.add(db_transcript)
    db.commit()
    db.refresh(db_transcript)
    return db_transcript


def get_transcripts_by_session(db: Session, session_id: int) -> List[Transcript]:
    """
    Get all transcripts for an audio session.
    """
    return db.query(Transcript).filter(Transcript.session_id == session_id).all()


def get_transcript(db: Session, transcript_id: int) -> Optional[Transcript]:
    """
    Get a transcript by ID.
    """
    return db.query(Transcript).filter(Transcript.id == transcript_id).first()


def delete_transcript(db: Session, transcript_id: int) -> bool:
    """
    Delete a transcript.
    """
    db_transcript = get_transcript(db, transcript_id)
    if db_transcript:
        db.delete(db_transcript)
        db.commit()
        return True
    return False
