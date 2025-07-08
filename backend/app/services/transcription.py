import asyncio
import logging
import os
from typing import List, Optional, Dict, Any

from openai import OpenAI
from pydantic import ValidationError

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
            # First try to use the mock transcription for development/testing
            if os.environ.get("USE_MOCK_TRANSCRIPTION", "false").lower() == "true":
                logger.info("Using mock transcription response for file")
                return self._create_mock_transcription()
                
            # Use OpenAI's Whisper model for transcription
            with open(file_path, "rb") as audio_file:
                # Call OpenAI API asynchronously
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
            
            # Process the response to extract segments
            segments = []
            
            # Handle the response format from OpenAI API v1.0.0+
            try:
                # Convert response to dictionary if it's an object
                if hasattr(response, 'model_dump'):
                    response_dict = response.model_dump()
                elif hasattr(response, '__dict__'):
                    response_dict = response.__dict__
                else:
                    response_dict = response  # Assume it's already a dict
                
                # Extract segments from the response dictionary
                response_segments = response_dict.get("segments", [])
                
                for segment in response_segments:
                    # Extract segment data
                    if isinstance(segment, dict):
                        # Dictionary access
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
                        # Object access
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
                # Create a fallback segment if parsing fails
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
            
            # Combine all segment texts to create the full transcript text
            full_text = " ".join([segment.text for segment in segments])
            
            return TranscriptionResult(
                session_id="",  # This would be filled in by the caller
                text=full_text,  # Add the required text field
                segments=segments,
                language="en",
                duration=response.duration if hasattr(response, 'duration') else None,
                is_final=True
            )
        
        except Exception as e:
            logger.error(f"Error transcribing audio file: {str(e)}")
            # If there's an API error, fall back to mock transcription
            if "insufficient_quota" in str(e) or "exceeded your current quota" in str(e):
                logger.warning("OpenAI API quota exceeded, using mock transcription instead")
                return self._create_mock_transcription()
            raise
    
    def _create_mock_transcription(self) -> TranscriptionResult:
        """
        Create a mock transcription result for testing purposes.
        
        Returns:
            TranscriptionResult with mock data
        """
        segments = [
            TranscriptSegment(
                text="Hello, this is a mock transcription for testing purposes.",
                start_time=0.0,
                end_time=3.0,
                confidence=0.98,
                speaker=None,
                is_prospect=False
            ),
            TranscriptSegment(
                text="The OpenAI API quota has been exceeded, so we're using this mock response instead.",
                start_time=3.1,
                end_time=7.0,
                confidence=0.97,
                speaker=None,
                is_prospect=False
            ),
            TranscriptSegment(
                text="This allows you to continue testing the application without being blocked by API limits.",
                start_time=7.1,
                end_time=11.0,
                confidence=0.99,
                speaker=None,
                is_prospect=False
            )
        ]
        
        # Combine all segment texts to create the full transcript text
        full_text = " ".join([segment.text for segment in segments])
        
        return TranscriptionResult(
            session_id="",  # This would be filled in by the caller
            text=full_text,  # Add the required text field
            segments=segments,
            language="en",
            duration=11,  # Duration based on the last segment's end time
            is_final=True
        )
    
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
            # First try to use the mock transcription for development/testing
            if os.environ.get("USE_MOCK_TRANSCRIPTION", "false").lower() == "true":
                logger.info("Using mock transcription response for chunk")
                return self._create_mock_transcription()
                
            # Use OpenAI's Whisper model for transcription
            with open(chunk_path, "rb") as audio_file:
                # Call OpenAI API asynchronously
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
            
            # Process the response to extract segments
            segments = []
            
            # Handle the response format from OpenAI API v1.0.0+
            try:
                # Convert response to dictionary if it's an object
                if hasattr(response, 'model_dump'):
                    response_dict = response.model_dump()
                elif hasattr(response, '__dict__'):
                    response_dict = response.__dict__
                else:
                    response_dict = response  # Assume it's already a dict
                
                # Extract segments from the response dictionary
                response_segments = response_dict.get("segments", [])
                
                for segment in response_segments:
                    # Extract segment data
                    if isinstance(segment, dict):
                        # Dictionary access
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
                        # Object access
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
                # Create a fallback segment if parsing fails
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
            
            # Combine all segment texts to create the full transcript text
            full_text = " ".join([segment.text for segment in segments])
            
            return TranscriptionResult(
                session_id="",  # This would be filled in by the caller
                text=full_text,  # Add the required text field
                segments=segments,
                language="en",  # Default to English as we set in the API request
                duration=response.duration if hasattr(response, 'duration') else None,
                is_final=is_final
            )
        
        except Exception as e:
            logger.error(f"Error transcribing audio chunk: {str(e)}")
            # If there's an API error, fall back to mock transcription
            if "insufficient_quota" in str(e) or "exceeded your current quota" in str(e):
                logger.warning("OpenAI API quota exceeded, using mock transcription instead")
                return self._create_mock_transcription()
            raise
    
    async def diarize_speakers(self, audio_path: str) -> List[Dict[str, Any]]:
        """
        Perform speaker diarization on an audio file.
        
        This is a placeholder for speaker diarization functionality.
        In a real implementation, this would use a specialized service or model
        for speaker diarization.
        
        Args:
            audio_path: Path to the audio file
            
        Returns:
            List of speaker segments with timing information
        """
        # This is a placeholder implementation
        # In a real system, you would integrate with a speaker diarization service
        # such as Pyannote, Google Cloud Speech-to-Text, or a custom model
        
        # Mock response for demonstration
        return [
            {
                "speaker": "speaker_1",
                "start_time": 0.0,
                "end_time": 5.0,
                "is_prospect": True
            },
            {
                "speaker": "speaker_2",
                "start_time": 5.1,
                "end_time": 10.0,
                "is_prospect": False
            }
        ]
