"""
Insight sharing API endpoints
Enables sharing insights from Dashboard to Nexus Community
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.insight import Insight
from app.models.post import Post
from app.schemas.insights import InsightShareRequest, InsightShareResponse, InsightListResponse
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/insights", tags=["insights"])


@router.post("/share", response_model=InsightShareResponse)
async def share_insight(
    share_data: InsightShareRequest,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Share an insight to Nexus Community
    
    Creates a post in Nexus feed linked to the insight
    
    Args:
        share_data: Insight sharing data
        user_id: Current user ID
        db: Database session
    
    Returns:
        Created post with shared insight
    """
    try:
        # Get the insight
        insight = db.query(Insight).filter(
            Insight.id == share_data.insight_id,
            Insight.user_id == user_id  # Ensure user owns the insight
        ).first()
        
        if not insight:
            raise HTTPException(
                status_code=404,
                detail="Insight not found or you don't have permission to share it"
            )
        
        # Mark insight as shared
        insight.shared = True
        
        # Create post linked to insight
        post = Post(
            id=str(uuid.uuid4()),
            author_id=user_id,
            content=share_data.caption or insight.summary or "Shared financial insight",
            media_urls=share_data.media_urls or [],
            media_type=share_data.media_type or "chart",
            is_shared_insight=True,
            insight_id=insight.id,
            tags=share_data.tags or []
        )
        
        db.add(post)
        db.commit()
        db.refresh(post)
        
        return InsightShareResponse(
            post_id=post.id,
            insight_id=insight.id,
            message="Insight shared successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error sharing insight: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Error sharing insight: {str(e)}"
        )


@router.get("/shared", response_model=InsightListResponse)
async def get_shared_insights(
    user_id: Optional[str] = None,  # TODO: Get from auth token
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    Get shared insights
    
    Args:
        user_id: Filter by user (optional, if None returns all shared)
        limit: Maximum number of results
        offset: Pagination offset
        db: Database session
    
    Returns:
        List of shared insights
    """
    try:
        query = db.query(Insight).filter(Insight.shared == True)
        
        if user_id:
            query = query.filter(Insight.user_id == user_id)
        
        insights = query.order_by(
            Insight.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        insights_data = []
        for insight in insights:
            insight_dict = {
                "id": str(insight.id),
                "user_id": insight.user_id,
                "summary": insight.summary,
                "tickers": insight.tickers or [],
                "shared": insight.shared,
                "created_at": insight.created_at.isoformat() if insight.created_at else None
            }
            insights_data.append(insight_dict)
        
        return InsightListResponse(
            insights=insights_data,
            count=len(insights_data),
            limit=limit,
            offset=offset
        )
        
    except Exception as e:
        logger.error(f"Error getting shared insights: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error getting shared insights: {str(e)}"
        )


@router.get("/{insight_id}/share-link")
async def get_share_link(
    insight_id: str,
    user_id: str = Query(default="anonymous", description="User ID"),  # TODO: Get from auth token
    db: Session = Depends(get_db)
):
    """
    Get a shareable link for an insight
    
    Args:
        insight_id: Insight ID
        user_id: Current user ID
        db: Database session
    
    Returns:
        Shareable link
    """
    insight = db.query(Insight).filter(
        Insight.id == insight_id,
        Insight.user_id == user_id
    ).first()
    
    if not insight:
        raise HTTPException(status_code=404, detail="Insight not found")
    
    # Generate shareable link (in production, this would be a proper URL)
    share_link = f"/insights/{insight_id}"
    
    return {
        "insight_id": insight_id,
        "share_link": share_link,
        "public": insight.shared
    }

