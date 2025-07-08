import asyncio
import logging
import os
from typing import List, Dict, Any

from openai import OpenAI

from app.core.config import settings
from app.schemas.audio import TranscriptionResult, TranscriptSegment

logger = logging.getLogger(__name__)

class TranscriptionService:
    """
    Service for transcribing audio using OpenAI's Whisper API.
    """
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        if self.api_key:
            self.client = OpenAI(api_key=self.api_key)
    
    async def transcribe_file(self, file_path: str) -> TranscriptionResult:
        """
        Transcribe a complete audio file.
        
        Args:
            file_path: Path to the audio file
            
        Returns:
            TranscriptionResult object with transcribed segments
        """
        if not self.api_key:
            raise ValueError("OpenAI API key is not configured")
        
        try:                
            with open(file_path, "rb") as audio_file:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        response_format="verbose_json",
                        temperature=0.0,
                        language="en"
                    )
                )
            
            segments = []
            
            try:
                if hasattr(response, 'model_dump'):
                    response_dict = response.model_dump()
                elif hasattr(response, '__dict__'):
                    response_dict = response.__dict__
                else:
                    response_dict = response
                
                response_segments = response_dict.get("segments", [])
                
                for segment in response_segments:
                    if isinstance(segment, dict):
                        segments.append(
                            TranscriptSegment(
                                text=segment.get("text", ""),
                                start_time=segment.get("start", 0.0),
                                end_time=segment.get("end", 0.0),
                                confidence=segment.get("confidence", 1.0),
                                speaker=None,
                                is_prospect=False
                            )
                        )
                    else:
                        segment_dict = segment.__dict__ if hasattr(segment, '__dict__') else {}
                        segments.append(
                            TranscriptSegment(
                                text=segment_dict.get("text", ""),
                                start_time=segment_dict.get("start", 0.0),
                                end_time=segment_dict.get("end", 0.0),
                                confidence=segment_dict.get("confidence", 1.0),
                                speaker=None,
                                is_prospect=False
                            )
                        )
            except Exception as e:
                logger.error(f"Error processing segments from response: {e}")
                segments.append(
                    TranscriptSegment(
                        text="[Error processing transcription response]",
                        start_time=0.0,
                        end_time=1.0,
                        confidence=1.0,
                        speaker=None,
                        is_prospect=False
                    )
                )
            
            full_text = " ".join([segment.text for segment in segments])
            
            return TranscriptionResult(
                session_id="",
                text=full_text,
                segments=segments,
                language="en",
                duration=response.duration if hasattr(response, 'duration') else None,
                is_final=True
            )
        
        except Exception as e:
            logger.error(f"Error transcribing audio file: {str(e)}")
            raise

    async def transcribe_chunk(self, chunk_path: str, is_final: bool = False) -> TranscriptionResult:
        """
        Transcribe a chunk of audio data.
        
        Args:
            chunk_path: Path to the audio chunk file
            is_final: Whether this is a final chunk for a segment
            
        Returns:
            TranscriptionResult object with transcribed segments
        """
        if not self.api_key:
            raise ValueError("OpenAI API key is not configured")
        
        try:  
            with open(chunk_path, "rb") as audio_file:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.audio.transcriptions.create(
                        file=audio_file,
                        model="whisper-1",
                        response_format="verbose_json",
                        temperature=0.0,
                        language="en"
                    )
                )
            
            segments = []
            
            try:
                if hasattr(response, 'model_dump'):
                    response_dict = response.model_dump()
                elif hasattr(response, '__dict__'):
                    response_dict = response.__dict__
                else:
                    response_dict = response
                
                response_segments = response_dict.get("segments", [])
                
                for segment in response_segments:
                    if isinstance(segment, dict):
                        segments.append(
                            TranscriptSegment(
                                text=segment.get("text", ""),
                                start_time=segment.get("start", 0.0),
                                end_time=segment.get("end", 0.0),
                                confidence=segment.get("confidence", 1.0),
                                speaker=None,
                                is_prospect=False
                            )
                        )
                    else:
                        segment_dict = segment.__dict__ if hasattr(segment, '__dict__') else {}
                        segments.append(
                            TranscriptSegment(
                                text=segment_dict.get("text", ""),
                                start_time=segment_dict.get("start", 0.0),
                                end_time=segment_dict.get("end", 0.0),
                                confidence=segment_dict.get("confidence", 1.0),
                                speaker=None,
                                is_prospect=False
                            )
                        )
            except Exception as e:
                logger.error(f"Error processing segments from response: {e}")
                segments.append(
                    TranscriptSegment(
                        text="[Error processing transcription response]",
                        start_time=0.0,
                        end_time=1.0,
                        confidence=1.0,
                        speaker=None,
                        is_prospect=False
                    )
                )
            
            full_text = " ".join([segment.text for segment in segments])
            
            return TranscriptionResult(
                session_id="",
                text=full_text,
                segments=segments,
                language="en",
                duration=response.duration if hasattr(response, 'duration') else None,
                is_final=is_final
            )
        
        except Exception as e:
            logger.error(f"Error transcribing audio chunk: {str(e)}")
            raise
