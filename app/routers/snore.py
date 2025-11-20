from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..database import get_db
from ..models import User, SnoreLog
from ..schemas import SnoreDetectionResponse, SnoreLogResponse
from ..auth import get_current_user
from ..ml_model import get_detector
from ..raspi_client import get_raspi_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/snore", tags=["Snoring Detection"])


@router.post("/detect", response_model=SnoreDetectionResponse)
async def detect_snoring(
    audio: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Detect snoring from uploaded audio file
    
    Accepts audio file (WAV, MP3, etc.)
    Returns detection result and triggers pump if snoring detected
    """
    try:
        # Validate file type
        if not audio.content_type.startswith('audio/'):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid file type. Please upload an audio file."
            )
        
        # Read audio data
        audio_data = await audio.read()
        audio_duration = len(audio_data) / (44100 * 2)  # Rough estimate
        
        # Get detector and make prediction
        detector = get_detector()
        snore_detected, confidence = detector.predict(audio_data)
        
        # Log the detection
        snore_log = SnoreLog(
            user_id=current_user.id,
            snore_detected=snore_detected,
            confidence=confidence,
            audio_duration=audio_duration
        )
        db.add(snore_log)
        db.commit()
        
        # Trigger pump if snoring detected
        pump_triggered = False
        if snore_detected and confidence >= 0.75:
            try:
                raspi_client = get_raspi_client()
                await raspi_client.trigger_pump_sequence()
                pump_triggered = True
                logger.info(f"Pump triggered for user {current_user.email}")
            except Exception as e:
                logger.error(f"Failed to trigger pump: {e}")
                # Don't fail the request if pump trigger fails
        
        # Prepare response message
        if snore_detected:
            message = f"Snoring detected with {confidence*100:.1f}% confidence"
            if pump_triggered:
                message += ". Pump activated."
        else:
            message = "No snoring detected"
        
        return SnoreDetectionResponse(
            snore_detected=snore_detected,
            confidence=confidence,
            message=message,
            pump_triggered=pump_triggered
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error during snore detection: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing audio: {str(e)}"
        )


@router.get("/logs", response_model=List[SnoreLogResponse])
async def get_snore_logs(
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's snoring detection logs"""
    logs = db.query(SnoreLog).filter(
        SnoreLog.user_id == current_user.id
    ).order_by(
        SnoreLog.timestamp.desc()
    ).limit(limit).offset(offset).all()
    
    return [SnoreLogResponse.model_validate(log) for log in logs]


@router.get("/stats")
async def get_snore_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's snoring statistics"""
    total_logs = db.query(SnoreLog).filter(
        SnoreLog.user_id == current_user.id
    ).count()
    
    snoring_detected = db.query(SnoreLog).filter(
        SnoreLog.user_id == current_user.id,
        SnoreLog.snore_detected == True
    ).count()
    
    avg_confidence = db.query(SnoreLog).filter(
        SnoreLog.user_id == current_user.id,
        SnoreLog.snore_detected == True
    ).with_entities(
        SnoreLog.confidence
    ).all()
    
    avg_conf_value = sum([c[0] for c in avg_confidence]) / len(avg_confidence) if avg_confidence else 0
    
    return {
        "total_detections": total_logs,
        "snoring_detected_count": snoring_detected,
        "no_snoring_count": total_logs - snoring_detected,
        "average_confidence": round(avg_conf_value, 3),
        "snoring_percentage": round((snoring_detected / total_logs * 100), 1) if total_logs > 0 else 0
    }

