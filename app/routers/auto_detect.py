from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime
import asyncio
import logging

from ..database import get_db
from ..models import User, SnoreLog, PumpLog
from ..schemas import MessageResponse
from ..auth import get_current_user
from ..raspi_client import get_raspi_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-detect", tags=["Auto Detection"])

# Global state for auto detection
auto_detection_state: Dict[str, any] = {
    "is_running": False,
    "user_id": None,
    "delay_minutes": 5,
    "stop_requested": False
}


@router.post("/start")
async def start_auto_detection(
    delay_minutes: int = 5,
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    Start automatic snoring detection
    
    Will continuously record 5-second audio clips and check for snoring
    When snoring is detected, triggers pump sequence and delays for specified minutes
    """
    global auto_detection_state
    
    if auto_detection_state["is_running"]:
        return {
            "status": "error",
            "message": "Auto detection is already running",
            "is_running": True
        }
    
    # Update state
    auto_detection_state["is_running"] = True
    auto_detection_state["user_id"] = str(current_user.id)
    auto_detection_state["delay_minutes"] = delay_minutes
    auto_detection_state["stop_requested"] = False
    
    logger.info(f"Auto detection started for user {current_user.email} with {delay_minutes} minute delay")
    
    return {
        "status": "success",
        "message": f"Auto detection started with {delay_minutes} minute delay",
        "is_running": True,
        "delay_minutes": delay_minutes
    }


@router.post("/stop")
async def stop_auto_detection(
    current_user: User = Depends(get_current_user)
):
    """Stop automatic snoring detection"""
    global auto_detection_state
    
    if not auto_detection_state["is_running"]:
        return {
            "status": "error",
            "message": "Auto detection is not running",
            "is_running": False
        }
    
    # Request stop
    auto_detection_state["stop_requested"] = True
    auto_detection_state["is_running"] = False
    
    logger.info(f"Auto detection stop requested by user {current_user.email}")
    
    return {
        "status": "success",
        "message": "Auto detection stopped",
        "is_running": False
    }


@router.get("/status")
async def get_auto_detection_status(
    current_user: User = Depends(get_current_user)
):
    """Get current auto detection status"""
    return {
        "status": "success",
        "is_running": auto_detection_state["is_running"],
        "delay_minutes": auto_detection_state["delay_minutes"],
        "user_id": auto_detection_state["user_id"]
    }


@router.post("/simulate-detection")
async def simulate_snoring_detection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate snoring detection and trigger pump sequence
    This endpoint simulates the detection without actual audio recording
    Used for testing the auto detection flow
    """
    try:
        # Log the simulated detection
        snore_log = SnoreLog(
            user_id=current_user.id,
            snore_detected=True,
            confidence=0.85,
            audio_duration=5.0
        )
        db.add(snore_log)
        db.commit()
        
        logger.info(f"Simulated snoring detected for user {current_user.email}")
        
        # Trigger pump sequence
        try:
            raspi_client = get_raspi_client()
            pump_response = await raspi_client.trigger_full_sequence()
            
            # Log pump activation
            pump_log = PumpLog(
                activated_by=current_user.id,
                status="success"
            )
            db.add(pump_log)
            db.commit()
            
            logger.info(f"Pump sequence triggered successfully: {pump_response}")
            
            return {
                "status": "success",
                "message": "Snoring detected! Pump sequence activated (Inflate 50s + Deflate 30s)",
                "snore_detected": True,
                "confidence": 0.85,
                "pump_triggered": True,
                "pump_response": pump_response
            }
        
        except Exception as pump_error:
            logger.error(f"Failed to trigger pump: {pump_error}")
            
            # Log failed pump activation
            pump_log = PumpLog(
                activated_by=current_user.id,
                status="failed",
                error_message=str(pump_error)
            )
            db.add(pump_log)
            db.commit()
            
            return {
                "status": "partial_success",
                "message": "Snoring detected but pump activation failed",
                "snore_detected": True,
                "confidence": 0.85,
                "pump_triggered": False,
                "error": str(pump_error)
            }
    
    except Exception as e:
        logger.error(f"Error in simulate detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

