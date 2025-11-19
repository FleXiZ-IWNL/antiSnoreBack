from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import User, PumpLog
from ..schemas import PumpTriggerRequest, PumpTriggerResponse, PumpLogResponse, MessageResponse
from ..auth import get_current_user
from ..raspi_client import get_raspi_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/pump", tags=["Pump Control"])


# @router.post("/trigger", response_model=PumpTriggerResponse)
# async def trigger_pump(
#     request: PumpTriggerRequest = PumpTriggerRequest(),
#     current_user: User = Depends(get_current_user),
#     db: Session = Depends(get_db)
# ):
@router.post("/trigger", response_model=PumpTriggerResponse)
async def trigger_pump(
    request: PumpTriggerRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Manually trigger the air pump on Raspberry Pi
    
    This endpoint allows manual testing of the pump
    """
    try:
        # Get Raspberry Pi client
        raspi_client = get_raspi_client()
        
        # Trigger pump
        # response = await raspi_client.trigger_pump_sequence()
                # Trigger pump (ส่ง duration ไปให้ Raspberry Pi)
                # Trigger pump โดยส่ง duration จาก request ไปให้ Raspberry Pi
                # Trigger pump โดยใช้ duration จาก request
        response = await raspi_client.trigger_pump_sequence(duration=request.duration)
        logger.info(f"Raspi pump trigger response: {response}")


        
        # Log the pump activation
        pump_log = PumpLog(
            activated_by=current_user.id,
            status="success"
        )
        db.add(pump_log)
        db.commit()
        
        logger.info(f"Pump manually triggered by user {current_user.email}")
        
        return PumpTriggerResponse(
            status="success",
            message="Pump triggered successfully",
            timestamp=datetime.utcnow()
        )
    
    except Exception as e:
        # Log the failed activation
        pump_log = PumpLog(
            activated_by=current_user.id,
            status="failed",
            error_message=str(e)
        )
        db.add(pump_log)
        db.commit()
        
        logger.error(f"Failed to trigger pump for user {current_user.email}: {e}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to trigger pump: {str(e)}"
        )


@router.get("/logs", response_model=List[PumpLogResponse])
async def get_pump_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's pump activation logs"""
    logs = db.query(PumpLog).filter(
        PumpLog.activated_by == current_user.id
    ).order_by(
        PumpLog.timestamp.desc()
    ).limit(limit).offset(offset).all()
    
    return [PumpLogResponse.model_validate(log) for log in logs]


@router.get("/status")
async def get_pump_status(
    current_user: User = Depends(get_current_user)
):
    """Get current pump status from Raspberry Pi"""
    try:
        raspi_client = get_raspi_client()
        status_response = await raspi_client.get_pump_status()
        return status_response
    except Exception as e:
        logger.error(f"Failed to get pump status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get pump status: {str(e)}"
        )

