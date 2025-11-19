from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict
import logging

from ..database import get_db
from ..models import User, SnoreLog, PumpLog
from ..auth import get_current_user
from ..raspi_client import get_raspi_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auto-detect", tags=["Auto Detection"])

# In-Memory State Store for Multiple Users
# Structure: { "user_id_string": { "is_running": bool, "delay_minutes": int } }
user_states: Dict[str, Dict] = {}

def get_user_state(user_id: str) -> Dict:
    """Get or initialize state for a specific user"""
    if user_id not in user_states:
        user_states[user_id] = {
            "is_running": False,
            "delay_minutes": 5
        }
    return user_states[user_id]

@router.post("/start")
async def start_auto_detection(
    delay_minutes: int = 5,
    current_user: User = Depends(get_current_user),
):
    """
    Start automatic snoring detection for the CURRENT USER.
    """
    user_id = str(current_user.id)
    state = get_user_state(user_id)
    
    state["is_running"] = True
    state["delay_minutes"] = delay_minutes
    
    logger.info(f"Auto detection ENABLED for user {current_user.email} (ID: {user_id})")
    
    return {
        "status": "success",
        "message": f"Auto detection enabled for {current_user.email}",
        "is_running": True,
        "delay_minutes": delay_minutes
    }


@router.post("/stop")
async def stop_auto_detection(
    current_user: User = Depends(get_current_user)
):
    """Stop automatic snoring detection for the CURRENT USER"""
    user_id = str(current_user.id)
    state = get_user_state(user_id)
    
    state["is_running"] = False
    
    logger.info(f"Auto detection DISABLED by user {current_user.email}")
    
    return {
        "status": "success",
        "message": "Auto detection disabled",
        "is_running": False
    }


@router.get("/status")
async def get_auto_detection_status(
    current_user: User = Depends(get_current_user)
):
    """Get status specific to the CURRENT USER"""
    user_id = str(current_user.id)
    state = get_user_state(user_id)
    
    return {
        "status": "success",
        "is_running": state["is_running"],
        "delay_minutes": state["delay_minutes"],
        "user_id": user_id
    }

@router.post("/simulate-detection")
async def simulate_snoring_detection(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate snoring detection for the current user
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
        
        # Note: In the Cloud/Client architecture, the Backend usually doesn't trigger the pump directly.
        # However, for simulation testing, if this is running locally, it might try.
        # If running on Render, this might fail if RaspiClient tries to connect to localhost.
        # We'll keep the logic but wrap safely.
        
        pump_response = None
        pump_triggered = False
        
        try:
            # Only try to trigger if we have a configured client URL (unlikely on Render towards generic client)
            # But let's assume this endpoint is for testing logic mainly.
            raspi_client = get_raspi_client()
            pump_response = await raspi_client.trigger_full_sequence()
            pump_triggered = True
            
            # Log pump activation
            pump_log = PumpLog(
                activated_by=current_user.id,
                status="success"
            )
            db.add(pump_log)
            db.commit()
            
        except Exception as pump_error:
            logger.warning(f"Simulate: Could not trigger pump directly (Normal on Cloud): {pump_error}")
            # Don't error out the whole request, just note it
        
        return {
            "status": "success",
            "message": "Snoring simulation recorded",
            "snore_detected": True,
            "confidence": 0.85,
            "pump_triggered": pump_triggered,
            "pump_response": pump_response
        }
    
    except Exception as e:
        logger.error(f"Error in simulate detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
