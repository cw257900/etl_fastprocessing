from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum, Text, ForeignKey, Boolean
from datetime import datetime
import enum
from app.core.database import Base

class ExceptionSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class DataException(Base):
    __tablename__ = "data_exceptions"
    
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("processing_jobs.id"))
    exception_type = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    severity = Column(Enum(ExceptionSeverity), nullable=False)
    additional_metadata = Column(JSON)
    stack_trace = Column(Text)
    resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer)
    resolution_notes = Column(Text)
    timestamp = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
