import logging
import os
import tempfile
from typing import Dict, Optional, Any
from sqlalchemy.orm import Session

from app.services.transcription import TranscriptionService
from app.services.keyword_detector import KeywordDetector
from app.services.notification import NotificationService
from app.schemas.notification import NotificationType
from app.schemas.audio import TranscriptionResult
from app.crud import audio as audio_crud

logger = logging.getLogger(__name__)

class AudioProcessor:
    """
    Service for processing audio files and chunks.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the AudioProcessor with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.transcription_service = TranscriptionService()
        self.keyword_detector = KeywordDetector(db)
        self.notification_service = NotificationService()
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.db = db
    
    async def process_audio_file_and_save(self, audio_data: bytes, session_id: str, file_format: str, file_path: str, db: Session) -> None:
        """
        Process a complete audio file and save results to the database.
        
        Args:
            audio_data: Raw audio data bytes
            session_id: Unique identifier for the session
            file_format: Format of the audio file (e.g., 'wav', 'mp3')
            file_path: Path where the audio file is stored
            db: Database session
        """
        try:
            with tempfile.NamedTemporaryFile(suffix=f'.{file_format}', delete=False) as temp_file:
                temp_file.write(audio_data)
                temp_path = temp_file.name
            
            try:
                transcription_result = await self.transcription_service.transcribe_file(temp_path)
                
                detected_keywords_list = []
                for segment in transcription_result.segments:
                    detected_keywords = await self.keyword_detector.detect_keywords(segment.text)
                    segment.detected_keywords = detected_keywords
                    detected_keywords_list.extend(detected_keywords)
                    
                    if detected_keywords:
                        for keyword in detected_keywords:
                            await self.notification_service.send_notification(
                                session_id=session_id,
                                notification_type=NotificationType.KEYWORD_DETECTED,
                                payload={
                                    "keyword": keyword,
                                    "segment": segment.dict(),
                                    "timestamp": segment.start_time
                                }
                            )
                
                full_text = " ".join([segment.text for segment in transcription_result.segments])
                db_transcription = TranscriptionResult(
                    session_id=session_id,
                    audio_file_path=file_path,
                    text=transcription_result.text,
                    language=transcription_result.language,
                    duration=transcription_result.duration,
                    meta_data={
                        "segments": [segment.dict() for segment in transcription_result.segments],
                        "detected_keywords": detected_keywords_list
                    },
                    is_final=True
                )
                
                audio_crud.create_transcript(db=db, session_id=session_id, transcription=db_transcription)
                
                await self.notification_service.send_notification(
                    session_id=session_id,
                    notification_type=NotificationType.TRANSCRIPTION_COMPLETE,
                    payload={
                        "transcript": full_text,
                        "detected_keywords": detected_keywords_list
                    }
                )
                
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            if str(e) == "TRANSCRIPTION_COMPLETE":
                logger.info(f"Audio processing completed: {str(e)}")
                await self.notification_service.send_notification(
                    session_id=session_id,
                    notification_type=NotificationType.TRANSCRIPTION_COMPLETE,
                    payload={"status": "complete"}
                )
            else:
                logger.error(f"Error processing audio file: {str(e)}")
                await self.notification_service.send_notification(
                    session_id=session_id,
                    notification_type=NotificationType.ERROR,
                    payload={"error": str(e)}
                )
            
    
    async def process_audio_chunk_and_save(self, chunk_data: bytes, session_id: str, sequence_number: int, timestamp: float, is_final: bool, file_path: Optional[str], db: Session) -> None:
        """
        Process a chunk of audio for real-time transcription and save results to the database.
        
        Args:
            chunk_data: Raw audio chunk data bytes
            session_id: Unique identifier for the session
            sequence_number: Sequence number of the chunk
            timestamp: Timestamp of the chunk in seconds
            is_final: Whether this is the final chunk in the sequence
            file_path: Path where the audio chunk is stored (if is_final is True)
            db: Database session
        """
        try:
            if session_id not in self.active_sessions:
                self.active_sessions[session_id] = {
                    "chunks": [],
                    "partial_transcripts": [],
                    "last_sequence": -1
                }
            
            session_data = self.active_sessions[session_id]
            
            if sequence_number <= session_data["last_sequence"]:
                logger.warning(f"Received out-of-order chunk for session {session_id}: {sequence_number} <= {session_data['last_sequence']}")
                return
            
            session_data["last_sequence"] = sequence_number
            
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
                temp_file.write(chunk_data)
                temp_path = temp_file.name
            
            try:
                transcription_result = await self.transcription_service.transcribe_chunk(temp_path, is_final)
                
                detected_keywords_list = []
                for segment in transcription_result.segments:
                    detected_keywords = await self.keyword_detector.detect_keywords(segment.text)
                    segment.detected_keywords = detected_keywords
                    detected_keywords_list.extend(detected_keywords)
                    
                    if detected_keywords:
                        for keyword in detected_keywords:
                            await self.notification_service.send_notification(
                                session_id=session_id,
                                notification_type=NotificationType.KEYWORD_DETECTED,
                                payload={
                                    "keyword": keyword,
                                    "segment": segment.dict(),
                                    "timestamp": segment.start_time
                                }
                            )
                
                session_data["chunks"].append({
                    "sequence_number": sequence_number,
                    "timestamp": timestamp,
                    "segments": transcription_result.segments
                })
                
                if is_final:
                    all_segments = []
                    for chunk in sorted(session_data["chunks"], key=lambda x: x["sequence_number"]):
                        all_segments.extend(chunk["segments"])
                    
                    full_text = " ".join([segment.text for segment in all_segments])
                    db_transcription = TranscriptionResult(
                        session_id=session_id,
                        audio_file_path=file_path,
                        text=full_text,
                        language="en",  # Default to English as TranscriptSegment doesn't have language attribute
                        duration=int(all_segments[-1].end_time) if all_segments else None,
                        meta_data={"segments": [segment.dict() for segment in all_segments]},
                        is_final=True
                    )
                    
                    audio_crud.create_transcript(db=db, session_id=session_id, transcription=db_transcription)
                    
                    await self.notification_service.send_notification(
                        session_id=session_id,
                        notification_type=NotificationType.TRANSCRIPTION_COMPLETE,
                        payload={
                            "transcript": full_text,
                            "detected_keywords": detected_keywords_list
                        }
                    )
                    
                    del self.active_sessions[session_id]
                else:
                    await self.notification_service.send_notification(
                        session_id=session_id,
                        notification_type=NotificationType.PARTIAL_TRANSCRIPTION,
                        payload={
                            "segments": [segment.dict() for segment in transcription_result.segments],
                            "detected_keywords": detected_keywords_list
                        }
                    )
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                    
        except Exception as e:
            logger.error(f"Error processing audio chunk: {str(e)}")
            await self.notification_service.send_notification(
                session_id=session_id,
                notification_type=NotificationType.ERROR,
                payload={"error": str(e)}
            )
