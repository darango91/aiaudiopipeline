import logging
import re
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.core.config import settings
from app.crud import keyword as keyword_crud
from app.models.keyword import Keyword, TalkingPoint

logger = logging.getLogger(__name__)

class KeywordDetector:
    """
    Service for detecting keywords in transcribed text and retrieving relevant talking points.
    Fetches keywords from the database and detects them in transcribed text.
    """
    
    def __init__(self, db: Session):
        """
        Initialize the KeywordDetector with a database session.
        
        Args:
            db: SQLAlchemy database session
        """
        self.db = db
        self.keywords_cache = {}
        self._load_keywords_from_db()
    
    def _load_keywords_from_db(self):
        """
        Load keywords and their talking points from the database.
        Stores them in a cache for efficient lookup during detection.
        """
        try:
            # Get all keywords from the database
            db_keywords = keyword_crud.get_keywords(self.db)
            
            # Build the keywords cache
            for keyword in db_keywords:
                # Get talking points for this keyword
                talking_points = keyword_crud.get_talking_points_by_keyword(self.db, keyword.id)
                
                # Format talking points for the cache
                formatted_talking_points = [
                    {
                        "id": tp.id,
                        "title": tp.title,
                        "content": tp.content,
                        "priority": tp.priority
                    } for tp in talking_points
                ]
                
                # Add to cache
                self.keywords_cache[keyword.text.lower()] = {
                    "id": keyword.id,
                    "text": keyword.text,
                    "description": keyword.description,
                    "threshold": keyword.threshold,
                    "talking_points": formatted_talking_points
                }
                
            logger.info(f"Loaded {len(self.keywords_cache)} keywords from database")
        except Exception as e:
            logger.error(f"Error loading keywords from database: {str(e)}")
            # If there's an error, use an empty cache
            self.keywords_cache = {}
    
    async def detect_keywords(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect keywords in the provided text.
        
        Args:
            text: The text to analyze for keywords
            
        Returns:
            List of detected keywords with confidence scores and talking points
        """
        if not text:
            return []
        
        detected_keywords = []
        
        # Convert text to lowercase for case-insensitive matching
        text_lower = text.lower()
        
        # Simple keyword matching using our database-backed cache
        for keyword_text, keyword_data in self.keywords_cache.items():
            threshold = keyword_data.get("threshold", settings.DEFAULT_KEYWORD_THRESHOLD)
            
            # Check for exact match
            if re.search(r'\b' + re.escape(keyword_text) + r'\b', text_lower):
                detected_keywords.append({
                    "id": keyword_data["id"],
                    "keyword": keyword_data["text"],
                    "description": keyword_data.get("description", ""),
                    "confidence": 1.0,  # Exact match has confidence 1.0
                    "talking_points": keyword_data.get("talking_points", [])
                })
            # Check for partial match (simplified)
            elif keyword_text in text_lower:
                # Only include if confidence exceeds threshold
                confidence = 0.8  # Partial match has lower confidence
                if confidence >= threshold:
                    detected_keywords.append({
                        "id": keyword_data["id"],
                        "keyword": keyword_data["text"],
                        "description": keyword_data.get("description", ""),
                        "confidence": confidence,
                        "talking_points": keyword_data.get("talking_points", [])
                    })
        
        # Sort by confidence (highest first)
        detected_keywords.sort(key=lambda x: x["confidence"], reverse=True)
        
        return detected_keywords
    
    async def get_talking_points(self, keyword: str) -> List[Dict[str, Any]]:
        """
        Get talking points for a specific keyword.
        
        Args:
            keyword: The keyword to get talking points for
            
        Returns:
            List of talking points for the keyword
        """
        keyword_lower = keyword.lower()
        
        # Check if keyword exists in our cache
        if keyword_lower in self.keywords_cache:
            return self.keywords_cache[keyword_lower].get("talking_points", [])
        
        # If not in cache, try to find it in the database
        try:
            db_keyword = keyword_crud.get_keyword_by_text(self.db, keyword)
            if db_keyword:
                # Get talking points for this keyword
                talking_points = keyword_crud.get_talking_points_by_keyword(self.db, db_keyword.id)
                
                # Format talking points
                formatted_talking_points = [
                    {
                        "id": tp.id,
                        "title": tp.title,
                        "content": tp.content,
                        "priority": tp.priority
                    } for tp in talking_points
                ]
                
                # Update cache for future use
                self.keywords_cache[keyword_lower] = {
                    "id": db_keyword.id,
                    "text": db_keyword.text,
                    "description": db_keyword.description,
                    "threshold": db_keyword.threshold,
                    "talking_points": formatted_talking_points
                }
                
                return formatted_talking_points
        except Exception as e:
            logger.error(f"Error fetching talking points for keyword '{keyword}': {str(e)}")
        
        return []
