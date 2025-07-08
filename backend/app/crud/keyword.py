from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.keyword import Keyword, TalkingPoint
from app.schemas.keyword import KeywordCreate, KeywordUpdate, TalkingPointCreate, TalkingPointUpdate


def get_keyword(db: Session, keyword_id: int) -> Optional[Keyword]:
    """Get a keyword by ID."""
    return db.query(Keyword).filter(Keyword.id == keyword_id).first()


def get_keyword_by_text(db: Session, text: str) -> Optional[Keyword]:
    """Get a keyword by text (case insensitive)."""
    return db.query(Keyword).filter(Keyword.text.ilike(text)).first()


def get_keywords(db: Session, skip: int = 0, limit: int = 100) -> List[Keyword]:
    """Get all keywords with pagination."""
    return db.query(Keyword).offset(skip).limit(limit).all()


def create_keyword(db: Session, keyword: KeywordCreate) -> Keyword:
    """Create a new keyword."""
    db_keyword = Keyword(
        text=keyword.text,
        description=keyword.description,
        threshold=keyword.threshold
    )
    db.add(db_keyword)
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


def update_keyword(db: Session, keyword_id: int, keyword_update: KeywordUpdate) -> Optional[Keyword]:
    """Update a keyword."""
    db_keyword = get_keyword(db, keyword_id)
    if not db_keyword:
        return None
    
    update_data = keyword_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_keyword, field, value)
    
    db.commit()
    db.refresh(db_keyword)
    return db_keyword


def delete_keyword(db: Session, keyword_id: int) -> bool:
    """Delete a keyword."""
    db_keyword = get_keyword(db, keyword_id)
    if not db_keyword:
        return False
    
    db.delete(db_keyword)
    db.commit()
    return True


def get_talking_point(db: Session, talking_point_id: int) -> Optional[TalkingPoint]:
    """Get a talking point by ID."""
    return db.query(TalkingPoint).filter(TalkingPoint.id == talking_point_id).first()


def get_talking_points_by_keyword(db: Session, keyword_id: int) -> List[TalkingPoint]:
    """Get all talking points for a keyword."""
    return db.query(TalkingPoint).filter(TalkingPoint.keyword_id == keyword_id).order_by(TalkingPoint.priority.desc()).all()


def create_talking_point(db: Session, keyword_id: int, talking_point: TalkingPointCreate) -> TalkingPoint:
    """Create a new talking point for a keyword."""
    db_talking_point = TalkingPoint(
        keyword_id=keyword_id,
        title=talking_point.title,
        content=talking_point.content,
        priority=talking_point.priority
    )
    db.add(db_talking_point)
    db.commit()
    db.refresh(db_talking_point)
    return db_talking_point


def update_talking_point(db: Session, talking_point_id: int, talking_point_update: TalkingPointUpdate) -> Optional[TalkingPoint]:
    """Update a talking point."""
    db_talking_point = get_talking_point(db, talking_point_id)
    if not db_talking_point:
        return None
    
    update_data = talking_point_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_talking_point, field, value)
    
    db.commit()
    db.refresh(db_talking_point)
    return db_talking_point


def delete_talking_point(db: Session, talking_point_id: int) -> bool:
    """Delete a talking point."""
    db_talking_point = get_talking_point(db, talking_point_id)
    if not db_talking_point:
        return False
    
    db.delete(db_talking_point)
    db.commit()
    return True
