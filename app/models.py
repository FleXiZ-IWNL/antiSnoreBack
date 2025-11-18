from sqlalchemy import Column, String, Boolean, Float, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from .database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    snore_logs = relationship("SnoreLog", back_populates="user", cascade="all, delete-orphan")
    pump_logs = relationship("PumpLog", back_populates="activated_by_user", cascade="all, delete-orphan")


class SnoreLog(Base):
    __tablename__ = "snore_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    snore_detected = Column(Boolean, nullable=False)
    confidence = Column(Float, nullable=False)
    audio_duration = Column(Float, nullable=True)
    
    # Relationship
    user = relationship("User", back_populates="snore_logs")


class PumpLog(Base):
    __tablename__ = "pump_logs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    activated_by = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    status = Column(String, nullable=False)  # 'success', 'failed', 'error'
    error_message = Column(String, nullable=True)
    
    # Relationship
    activated_by_user = relationship("User", back_populates="pump_logs")

