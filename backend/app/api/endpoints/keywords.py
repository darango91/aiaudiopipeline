from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.keyword import (
    Keyword, KeywordCreate, KeywordUpdate, 
    KeywordWithTalkingPoints, TalkingPoint, 
    TalkingPointCreate, TalkingPointUpdate
)
from app.crud import keyword as keyword_crud

router = APIRouter()


@router.get("/", response_model=List[Keyword])
def get_keywords(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Retrieve all keywords.
    """
    return keyword_crud.get_keywords(db=db, skip=skip, limit=limit)


@router.post("/", response_model=Keyword, status_code=status.HTTP_201_CREATED)
def create_keyword(
    keyword: KeywordCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new keyword.
    """
    # Check if keyword with same text already exists
    db_keyword = keyword_crud.get_keyword_by_text(db=db, text=keyword.text)
    if db_keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Keyword with text '{keyword.text}' already exists"
        )
    return keyword_crud.create_keyword(db=db, keyword=keyword)


@router.get("/{keyword_id}", response_model=KeywordWithTalkingPoints)
def get_keyword(
    keyword_id: int = Path(..., title="The ID of the keyword to get"),
    db: Session = Depends(get_db)
):
    """
    Get a specific keyword by ID, including its talking points.
    """
    db_keyword = keyword_crud.get_keyword(db=db, keyword_id=keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found"
        )
    
    # Get talking points for this keyword
    talking_points = keyword_crud.get_talking_points_by_keyword(db=db, keyword_id=keyword_id)
    
    # Create response with keyword and talking points
    result = db_keyword.__dict__
    result["talking_points"] = talking_points
    
    return result


@router.put("/{keyword_id}", response_model=Keyword)
def update_keyword(
    keyword_update: KeywordUpdate,
    keyword_id: int = Path(..., title="The ID of the keyword to update"),
    db: Session = Depends(get_db)
):
    """
    Update a keyword by ID.
    """
    db_keyword = keyword_crud.get_keyword(db=db, keyword_id=keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found"
        )
    
    updated = keyword_crud.update_keyword(db=db, keyword_id=keyword_id, keyword_update=keyword_update)
    return updated


@router.delete("/{keyword_id}", response_model=dict)
def delete_keyword(
    keyword_id: int = Path(..., title="The ID of the keyword to delete"),
    db: Session = Depends(get_db)
):
    """
    Delete a keyword by ID.
    """
    db_keyword = keyword_crud.get_keyword(db=db, keyword_id=keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found"
        )
    
    success = keyword_crud.delete_keyword(db=db, keyword_id=keyword_id)
    if success:
        return {"message": f"Keyword with ID {keyword_id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete keyword with ID {keyword_id}"
        )


@router.post("/{keyword_id}/talking-points/", response_model=TalkingPoint, status_code=status.HTTP_201_CREATED)
def create_talking_point(
    talking_point: TalkingPointCreate,
    keyword_id: int = Path(..., title="The ID of the keyword to add a talking point to"),
    db: Session = Depends(get_db)
):
    """
    Create a new talking point for a specific keyword.
    """
    # Check if keyword exists
    db_keyword = keyword_crud.get_keyword(db=db, keyword_id=keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found"
        )
    
    # Create talking point
    return keyword_crud.create_talking_point(db=db, keyword_id=keyword_id, talking_point=talking_point)


@router.put("/{keyword_id}/talking-points/{talking_point_id}", response_model=TalkingPoint)
def update_talking_point(
    talking_point_update: TalkingPointUpdate,
    keyword_id: int = Path(..., title="The ID of the keyword"),
    talking_point_id: int = Path(..., title="The ID of the talking point to update"),
    db: Session = Depends(get_db)
):
    """
    Update a talking point by ID.
    """
    # Check if keyword exists
    db_keyword = keyword_crud.get_keyword(db=db, keyword_id=keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found"
        )
    
    # Check if talking point exists and belongs to the keyword
    db_talking_point = keyword_crud.get_talking_point(db=db, talking_point_id=talking_point_id)
    if not db_talking_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Talking point with ID {talking_point_id} not found"
        )
    
    if db_talking_point.keyword_id != keyword_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Talking point with ID {talking_point_id} does not belong to keyword with ID {keyword_id}"
        )
    
    # Update talking point
    return keyword_crud.update_talking_point(db=db, talking_point_id=talking_point_id, talking_point_update=talking_point_update)


@router.delete("/{keyword_id}/talking-points/{talking_point_id}", response_model=dict)
def delete_talking_point(
    keyword_id: int = Path(..., title="The ID of the keyword"),
    talking_point_id: int = Path(..., title="The ID of the talking point to delete"),
    db: Session = Depends(get_db)
):
    """
    Delete a talking point by ID.
    """
    # Check if keyword exists
    db_keyword = keyword_crud.get_keyword(db=db, keyword_id=keyword_id)
    if not db_keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Keyword with ID {keyword_id} not found"
        )
    
    # Check if talking point exists and belongs to the keyword
    db_talking_point = keyword_crud.get_talking_point(db=db, talking_point_id=talking_point_id)
    if not db_talking_point:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Talking point with ID {talking_point_id} not found"
        )
    
    if db_talking_point.keyword_id != keyword_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Talking point with ID {talking_point_id} does not belong to keyword with ID {keyword_id}"
        )
    
    # Delete talking point
    success = keyword_crud.delete_talking_point(db=db, talking_point_id=talking_point_id)
    if success:
        return {"message": f"Talking point with ID {talking_point_id} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete talking point with ID {talking_point_id}"
        )
