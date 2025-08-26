from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, Text, ForeignKey
from datetime import datetime
import enum
from app.core.database import Base

class JobStatus(enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class ProcessingJob(Base):
    __tablename__ = "processing_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text)
    source_id = Column(Integer, ForeignKey("data_sources.id"))
    status = Column(Enum(JobStatus), default=JobStatus.PENDING)
    input_data = Column(JSON)
    output_data = Column(JSON)
    transformation_rules = Column(JSON)
    error_message = Column(Text)
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    created_by = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
