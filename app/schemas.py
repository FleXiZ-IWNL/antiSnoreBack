from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# ==================== Auth Schemas ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ==================== Snore Detection Schemas ====================

class SnoreDetectionRequest(BaseModel):
    audio_duration: Optional[float] = None


class SnoreDetectionResponse(BaseModel):
    snore_detected: bool
    confidence: float
    message: str
    pump_triggered: bool = False


class SnoreLogResponse(BaseModel):
    id: UUID
    timestamp: datetime
    snore_detected: bool
    confidence: float
    audio_duration: Optional[float]
    
    class Config:
        from_attributes = True


# ==================== Pump Schemas ====================

class PumpTriggerRequest(BaseModel):
    force: bool = False


class PumpTriggerResponse(BaseModel):
    status: str
    message: str
    timestamp: datetime


class PumpLogResponse(BaseModel):
    id: UUID
    timestamp: datetime
    status: str
    error_message: Optional[str]
    
    class Config:
        from_attributes = True


# ==================== General Schemas ====================

class MessageResponse(BaseModel):
    message: str
    status: str = "success"

