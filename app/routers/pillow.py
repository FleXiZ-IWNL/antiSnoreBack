from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
import logging

from ..database import get_db
from ..models import User
from ..auth import get_current_user
from ..raspi_client import get_raspi_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pillow", tags=["Pillow Control"])


class PillowLevelRequest(BaseModel):
    level: int


@router.post("/level")
async def set_pillow_level(
    request: PillowLevelRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Set pillow level (0-3)
    
    Levels:
    - 0: Flat (Deflate 30s)
    - 1: Low (Inflate 25s)
    - 2: Medium (Inflate 40s)
    - 3: High (Inflate 60s)
    """
    if request.level not in [0, 1, 2, 3]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid level. Must be 0, 1, 2, or 3"
        )
    
    try:
        raspi_client = get_raspi_client()
        response = await raspi_client.set_pillow_level(request.level)
        
        logger.info(f"Pillow level set to {request.level} by user {current_user.email}")
        
        return {
            "status": "success",
            "message": response.get('message'),
            "level": request.level,
            "description": response.get('description'),
            "duration": response.get('duration'),
            "timestamp": datetime.utcnow()
        }
    
    except Exception as e:
        logger.error(f"Failed to set pillow level: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set pillow level: {str(e)}"
        )


@router.get("/levels")
async def get_pillow_levels(current_user: User = Depends(get_current_user)):
    """Get available pillow levels and their descriptions"""
    return {
        "status": "success",
        "levels": [
            {
                "level": 0,
                "name": "Flat",
                "description": "Deflate completely",
                "pump": 2,
                "duration": 30,
                "icon": "⬇️"
            },
            {
                "level": 1,
                "name": "Low",
                "description": "Low elevation",
                "pump": 1,
                "duration": 25,
                "icon": "📏"
            },
            {
                "level": 2,
                "name": "Medium",
                "description": "Medium elevation",
                "pump": 1,
                "duration": 40,
                "icon": "📐"
            },
            {
                "level": 3,
                "name": "High",
                "description": "High elevation",
                "pump": 1,
                "duration": 60,
                "icon": "📊"
            }
        ]
    }

