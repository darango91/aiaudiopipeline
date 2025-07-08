import os
import uuid
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, BackgroundTasks
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.schemas.audio import (
    AudioSession, AudioSessionCreate, AudioSessionUpdate, 
    TranscriptionResult, Transcript
)
from app.services.audio_processor import AudioProcessor
from app.services.transcription import TranscriptionService
from app.crud import audio as audio_crud

router = APIRouter()
# We'll create the AudioProcessor with a database session in each endpoint
transcription_service = TranscriptionService()


@router.post("/sessions", response_model=AudioSession)
def create_session(
    session: AudioSessionCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new audio session.
    """
    db_session = audio_crud.create_audio_session(db=db, session=session)
    return db_session


@router.get("/sessions/{session_id}", response_model=AudioSession)
def get_session(
    session_id: str,
    db: Session = Depends(get_db)
):
    """
    Get information about a specific audio session.
    """
    db_session = audio_crud.get_audio_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Audio session not found")
    return db_session


@router.put("/sessions/{session_id}", response_model=AudioSession)
def update_session(
    session_id: str,
    session_update: AudioSessionUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing audio session.
    """
    db_session = audio_crud.update_audio_session(db=db, session_id=session_id, session_update=session_update)
    if not db_session:
        raise HTTPException(status_code=404, detail="Audio session not found")
    return db_session


@router.post("/upload/", response_model=TranscriptionResult)
async def upload_audio(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    audio_file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for processing and transcription.
    """
    # Check if session exists
    db_session = audio_crud.get_audio_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Audio session not found")
        
    # Validate file size
    file_size = os.fstat(audio_file.file.fileno()).st_size
    max_size = settings.MAX_AUDIO_SIZE_MB * 1024 * 1024  # Convert MB to bytes
    
    if file_size > max_size:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Maximum size allowed is {settings.MAX_AUDIO_SIZE_MB}MB"
        )
    
    # Validate file format
    file_extension = audio_file.filename.split('.')[-1].lower()
    if file_extension not in settings.SUPPORTED_AUDIO_FORMATS:
        raise HTTPException(
            status_code=415,
            detail=f"Unsupported file format. Supported formats: {', '.join(settings.SUPPORTED_AUDIO_FORMATS)}"
        )
    
    # Generate a filename for storage
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    filename = f"{session_id}_{timestamp}.{file_extension}"
    file_path = os.path.join(settings.AUDIO_STORAGE_PATH, filename)
    
    # Process audio file
    try:
        # Read file content
        content = await audio_file.read()
        
        # Save file to disk if storage path exists
        os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create initial transcription result
        transcription_result = TranscriptionResult(
            session_id=session_id,
            audio_file_path=file_path,
            text="",  # Will be updated by background task
            is_final=False
        )
        
        # Create AudioProcessor with database session
        audio_processor = AudioProcessor(db)
        
        # Process audio in the background and update the database when done
        background_tasks.add_task(
            audio_processor.process_audio_file_and_save,
            content,
            session_id,
            file_extension,
            file_path,
            db
        )
        
        return transcription_result
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio: {str(e)}"
        )


@router.post("/chunks/", response_model=TranscriptionResult)
async def process_audio_chunk(
    background_tasks: BackgroundTasks,
    session_id: str = Form(...),
    sequence_number: int = Form(...),
    timestamp: float = Form(...),
    is_final: bool = Form(False),
    audio_chunk: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Process a chunk of audio for real-time transcription.
    """
    # Check if session exists
    db_session = audio_crud.get_audio_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Audio session not found")
        
    try:
        # Read chunk content
        content = await audio_chunk.read()
        
        # Generate a filename for storage if it's the final chunk
        file_path = None
        if is_final:
            file_extension = audio_chunk.filename.split('.')[-1].lower() if '.' in audio_chunk.filename else 'wav'
            timestamp_str = datetime.utcnow().strftime("%Y%m%d%H%M%S")
            filename = f"{session_id}_chunk_{sequence_number}_{timestamp_str}.{file_extension}"
            file_path = os.path.join(settings.AUDIO_STORAGE_PATH, filename)
            
            # Save file to disk if storage path exists
            os.makedirs(settings.AUDIO_STORAGE_PATH, exist_ok=True)
            with open(file_path, "wb") as f:
                f.write(content)
        
        # Create initial transcription result
        transcription_result = TranscriptionResult(
            session_id=session_id,
            audio_file_path=file_path,
            text="",  # Will be updated by background task
            is_final=is_final
        )
        
        # Create AudioProcessor with database session
        audio_processor = AudioProcessor(db)
        
        # Process audio chunk in the background and update the database when done
        background_tasks.add_task(
            audio_processor.process_audio_chunk_and_save,
            content,
            session_id,
            sequence_number,
            timestamp,
            is_final,
            file_path,
            db
        )
        
        return transcription_result
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing audio chunk: {str(e)}"
        )


@router.get("/sessions/{session_id}/transcripts", response_model=List[Transcript])
def get_transcripts(
    session_id: str,
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Get transcripts for a specific session, optionally filtered by time range.
    """
    # Check if session exists
    db_session = audio_crud.get_audio_session(db=db, session_id=session_id)
    if not db_session:
        raise HTTPException(status_code=404, detail="Audio session not found")
        
    # Get transcripts from database
    transcripts = audio_crud.get_transcripts_by_session(db=db, session_id=db_session.id)
    
    # Apply time range filter if provided
    if start_time is not None or end_time is not None:
        filtered_transcripts = []
        for transcript in transcripts:
            # Extract segment times from metadata
            segments = transcript.meta_data.get("segments", []) if transcript.meta_data else []
            
            # Check if any segment falls within the time range
            for segment in segments:
                segment_start = segment.get("start_time", 0)
                segment_end = segment.get("end_time", 0)
                
                # Apply filters
                if start_time is not None and segment_end < start_time:
                    continue
                if end_time is not None and segment_start > end_time:
                    continue
                    
                filtered_transcripts.append(transcript)
                break
        
        return filtered_transcripts
    
    return transcripts
